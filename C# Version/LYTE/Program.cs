using NAudio.Wave;
using YoutubeExplode;
using YoutubeExplode.Converter;

class Program {
    static YoutubeClient youtube = new YoutubeClient();

    static readonly Queue<string> playQueue = new();
    static readonly object queueLock = new();

    static IWavePlayer outputDevice;
    static AudioFileReader audioFile;

    static string outputDir = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.MyVideos),
        "LYTE"
    );


    static string ffmpegPath = @"E:\C#\LYTE_Test\LYTE_Test\FFmpeg\ffmpeg.exe";

    static async Task Main() {
        Directory.CreateDirectory(outputDir);

        string streamID = "jfKfPfyJRdk";
        using var chat = Pytchat.Pytchat.Create(streamID);

        Console.WriteLine("LYTE started. Listening for !queue <videoID>");

        while (chat.IsAlive()) {
            var chatData = await chat.GetAsync();

            foreach (var item in chatData.Items) {
                string message = item.Message;
                if (string.IsNullOrWhiteSpace(message))
                    continue;

                var parts = message.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length != 2)
                    continue;

                if (parts[0] != "!queue")
                    continue;

                string videoID = parts[1];
                _ = HandleQueueRequest(videoID); // fire-and-forget
            }
        }
    }

    static async Task HandleQueueRequest(string videoID) {
        string videoURL = $"https://youtube.com/watch?v={videoID}";

        YoutubeExplode.Videos.Video video;

        try {
            video = await youtube.Videos.GetAsync(videoURL);
            Console.WriteLine($"Queued: {video.Title}");
        } catch {
            Console.WriteLine($"Invalid video ID: {videoID}");
            return;
        }


        string outputPath = Path.Combine(outputDir, $"{video.Title}.mp3");


        Console.WriteLine("output: " + outputPath);

        if (!File.Exists(outputPath)) {
            try {
                await youtube.Videos.DownloadAsync(
                    videoURL,
                    outputPath,
                    o => o
                        .SetContainer("mp3")
                        .SetPreset(ConversionPreset.UltraFast)
                        .SetFFmpegPath(ffmpegPath)
                );
            } catch (Exception e) {
                Console.WriteLine($"Download failed for {videoID}");
                Console.WriteLine(e.Message);
                return;
            }
        }

        lock (queueLock) {
            playQueue.Enqueue(outputPath);
        }

        if (outputDevice == null || outputDevice.PlaybackState != PlaybackState.Playing) {
            PlayNext();
        }
    }

    static void PlayNext() {
        string nextTrack = null;

        lock (queueLock) {
            if (playQueue.Count > 0)
                nextTrack = playQueue.Dequeue();
        }

        if (nextTrack == null)
            return;

        StopPlayback();

        audioFile = new AudioFileReader(nextTrack);
        outputDevice = new WaveOutEvent();
        outputDevice.Init(audioFile);

        outputDevice.PlaybackStopped += (s, e) => {
            PlayNext();
        };

        outputDevice.Play();
        Console.WriteLine($"Now playing: {Path.GetFileName(nextTrack)}");
    }

    static void StopPlayback() {
        outputDevice?.Stop();
        outputDevice?.Dispose();
        audioFile?.Dispose();

        outputDevice = null;
        audioFile = null;
    }
}
