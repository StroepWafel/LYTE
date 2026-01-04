using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace Pytchat {
    public class ChatItem {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "";

        [JsonPropertyName("id")]
        public string Id { get; set; } = "";

        [JsonPropertyName("message")]
        public string Message { get; set; } = "";

        [JsonPropertyName("messageEx")]
        public object MessageEx { get; set; } = new List<object>();

        [JsonPropertyName("timestamp")]
        public long Timestamp { get; set; }

        [JsonPropertyName("datetime")]
        public string DateTime { get; set; } = "";

        [JsonPropertyName("elapsedTime")]
        public string ElapsedTime { get; set; } = "";

        [JsonPropertyName("amountValue")]
        public double AmountValue { get; set; }

        [JsonPropertyName("amountString")]
        public string AmountString { get; set; } = "";

        [JsonPropertyName("currency")]
        public string Currency { get; set; } = "";

        [JsonPropertyName("bgColor")]
        public long BgColor { get; set; }

        [JsonPropertyName("author")]
        public Author Author { get; set; } = new Author();

        [JsonPropertyName("colors")]
        public Colors Colors { get; set; }

        [JsonPropertyName("sticker")]
        public string Sticker { get; set; }
    }

    public class Author {
        [JsonPropertyName("name")]
        public string Name { get; set; } = "";

        [JsonPropertyName("channelId")]
        public string ChannelId { get; set; } = "";

        [JsonPropertyName("channelUrl")]
        public string ChannelUrl { get; set; } = "";

        [JsonPropertyName("imageUrl")]
        public string ImageUrl { get; set; } = "";

        [JsonPropertyName("badgeUrl")]
        public string BadgeUrl { get; set; } = "";

        [JsonPropertyName("isVerified")]
        public bool IsVerified { get; set; }

        [JsonPropertyName("isChatOwner")]
        public bool IsChatOwner { get; set; }

        [JsonPropertyName("isChatSponsor")]
        public bool IsChatSponsor { get; set; }

        [JsonPropertyName("isChatModerator")]
        public bool IsChatModerator { get; set; }
    }

    public class Colors {
        [JsonPropertyName("headerBackgroundColor")]
        public long HeaderBackgroundColor { get; set; }

        [JsonPropertyName("headerTextColor")]
        public long HeaderTextColor { get; set; }

        [JsonPropertyName("bodyBackgroundColor")]
        public long BodyBackgroundColor { get; set; }

        [JsonPropertyName("bodyTextColor")]
        public long BodyTextColor { get; set; }

        [JsonPropertyName("timestampColor")]
        public long TimestampColor { get; set; }

        [JsonPropertyName("authorNameTextColor")]
        public long AuthorNameTextColor { get; set; }

        [JsonPropertyName("moneyChipBackgroundColor")]
        public long MoneyChipBackgroundColor { get; set; }

        [JsonPropertyName("moneyChipTextColor")]
        public long MoneyChipTextColor { get; set; }

        [JsonPropertyName("backgroundColor")]
        public long BackgroundColor { get; set; }
    }

    public class ChatData {
        [JsonPropertyName("items")]
        public List<ChatItem> Items { get; set; } = new List<ChatItem>();

        [JsonPropertyName("interval")]
        public double Interval { get; set; }

        [JsonPropertyName("abs_diff")]
        public double AbsDiff { get; set; }

        [JsonPropertyName("itemcount")]
        public int ItemCount { get; set; }

        public string Json() {
            var options = new JsonSerializerOptions {
                WriteIndented = false,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };
            return JsonSerializer.Serialize(Items, options);
        }
    }

    // Utility functions
    public static class Utils {
        private static readonly Regex PatternYtUrl = new Regex(@"(?<=(v|V)/)|(?<=be/)|(?<=(\?|&)v=)|(?<=embed/)([\w-]+)", RegexOptions.Compiled);
        private static readonly Regex PatternChannel = new Regex(@"\\""channelId\\"":\\""(.{24})\\""", RegexOptions.Compiled);
        private static readonly Regex PatternMChannel = new Regex(@"""channelId"":""(.{24})""", RegexOptions.Compiled);
        private const int YtVideoIdLength = 11;

        public static string ExtractVideoId(string urlOrId) {
            urlOrId = urlOrId.Replace("[", "").Replace("]", "");

            if (urlOrId.Length == YtVideoIdLength)
                return urlOrId;

            var match = PatternYtUrl.Match(urlOrId);
            if (!match.Success)
                throw new InvalidOperationException($"Invalid video id: {urlOrId}");

            var videoId = match.Groups[match.Groups.Count - 1].Value;
            if (string.IsNullOrEmpty(videoId) || videoId.Length != YtVideoIdLength)
                throw new InvalidOperationException($"Invalid video id: {urlOrId}");

            return videoId;
        }

        public static async Task<string> GetChannelIdAsync(HttpClient client, string videoId) {
            try {
                var url = $"https://www.youtube.com/embed/{Uri.EscapeDataString(videoId)}";
                var response = await client.GetStringAsync(url);
                var match = PatternChannel.Match(response);
                if (match.Success)
                    return match.Groups[1].Value;
            } catch { }

            // Try mobile version
            try {
                var url = $"https://m.youtube.com/watch?v={Uri.EscapeDataString(videoId)}";
                var response = await client.GetStringAsync(url);
                var match = PatternMChannel.Match(response);
                if (match.Success)
                    return match.Groups[1].Value;
            } catch { }

            throw new InvalidOperationException($"Cannot find channel id for video id: {videoId}");
        }

        public static string GetClientVersion() {
            var yesterday = DateTime.Now.AddDays(-1);
            return $"2.{yesterday:yyyyMMdd}.01.00";
        }

        public static Dictionary<string, object> GetParam(string continuation, bool replay = false, int offsetMs = 0, string dat = "") {
            if (offsetMs < 0)
                offsetMs = 0;

            var param = new Dictionary<string, object> {
                ["context"] = new Dictionary<string, object> {
                    ["client"] = new Dictionary<string, object> {
                        ["visitorData"] = dat,
                        ["userAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63",
                        ["clientName"] = "WEB",
                        ["clientVersion"] = GetClientVersion()
                    }
                },
                ["continuation"] = continuation
            };

            if (replay) {
                ((Dictionary<string, object>)param["context"])["currentPlayerState"] = new Dictionary<string, object> {
                    ["playerOffsetMs"] = offsetMs.ToString()
                };
            }

            return param;
        }
    }

    // Encoding functions for parameter generation
    public static class Encoder {
        public static byte[] Vn(long val) {
            if (val < 0)
                throw new ArgumentException("Value must be non-negative");

            var buf = new List<byte>();
            while ((val >> 7) != 0) {
                var m = (byte)(val & 0xFF | 0x80);
                buf.Add(m);
                val >>= 7;
            }
            buf.Add((byte)val);
            return buf.ToArray();
        }

        public static byte[] Tp(int a, int b, byte[] ary) {
            return Vn((b << 3) | a).Concat(ary).ToArray();
        }

        public static byte[] Rs(int a, byte[] ary) {
            return Tp(2, a, Vn(ary.Length).Concat(ary).ToArray());
        }

        public static byte[] Rs(int a, string str) {
            return Rs(a, Encoding.UTF8.GetBytes(str));
        }

        public static byte[] Nm(int a, long val) {
            return Tp(0, a, Vn(val));
        }
    }

    // Parameter generation
    public static class LiveParam {
        private static string Header(string videoId, string channelId) {
            var s1_3 = Encoder.Rs(1, videoId);
            var s1_5 = Encoder.Rs(1, channelId).Concat(Encoder.Rs(2, videoId)).ToArray();
            var s1 = Encoder.Rs(3, s1_3).Concat(Encoder.Rs(5, s1_5)).ToArray();
            var s3 = Encoder.Rs(48687757, Encoder.Rs(1, videoId));
            var headerReplay = Encoder.Rs(1, s1).Concat(Encoder.Rs(3, s3)).Concat(Encoder.Nm(4, 1)).ToArray();
            var base64 = Convert.ToBase64String(headerReplay);
            return base64.Replace("+", "-").Replace("/", "_").TrimEnd('=');
        }

        private static long[] Times(int pastSec) {
            var random = new Random();
            var n = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            var ts1 = n - random.NextDouble() * 3;
            var ts2 = n - random.NextDouble() * 0.98 - 0.01;
            var ts3 = n - pastSec + random.NextDouble();
            var ts4 = n - random.NextDouble() * (60 * 60 - 10 * 60) - 10 * 60;
            var ts5 = n - random.NextDouble() * 0.98 - 0.01;
            return new[] { ts1, ts2, ts3, ts4, ts5 }.Select(x => (long)(x * 1000000)).ToArray();
        }

        private static string Build(string videoId, string channelId, long[] times, bool topchatOnly) {
            var chattype = topchatOnly ? 4 : 1;
            var b1 = Encoder.Nm(1, 0);
            var b2 = Encoder.Nm(2, 0);
            var b3 = Encoder.Nm(3, 0);
            var b4 = Encoder.Nm(4, 0);
            var b7 = Encoder.Rs(7, "");
            var b8 = Encoder.Nm(8, 0);
            var b9 = Encoder.Rs(9, "");
            var timestamp2 = Encoder.Nm(10, times[1]);
            var b11 = Encoder.Nm(11, 3);
            var b15 = Encoder.Nm(15, 0);

            var header = Encoder.Rs(3, Header(videoId, channelId));
            var timestamp1 = Encoder.Nm(5, times[0]);
            var s6 = Encoder.Nm(6, 0);
            var s7 = Encoder.Nm(7, 0);
            var s8 = Encoder.Nm(8, 1);
            var body = Encoder.Rs(9, b1.Concat(b2).Concat(b3).Concat(b4).Concat(b7).Concat(b8).Concat(b9).Concat(timestamp2).Concat(b11).Concat(b15).ToArray());
            var timestamp3 = Encoder.Nm(10, times[2]);
            var timestamp4 = Encoder.Nm(11, times[3]);
            var s13 = Encoder.Nm(13, chattype);
            var chattypeField = Encoder.Rs(16, Encoder.Nm(1, chattype));
            var s17 = Encoder.Nm(17, 0);
            var str19 = Encoder.Rs(19, Encoder.Nm(1, 0));
            var timestamp5 = Encoder.Nm(20, times[4]);
            var entity = header.Concat(timestamp1).Concat(s6).Concat(s7).Concat(s8).Concat(body)
                .Concat(timestamp3).Concat(timestamp4).Concat(s13).Concat(chattypeField).Concat(s17).Concat(str19).Concat(timestamp5).ToArray();
            var continuation = Encoder.Rs(119693434, entity);
            var base64 = Convert.ToBase64String(continuation);
            var urlSafe = base64.Replace("+", "-").Replace("/", "_").TrimEnd('=');
            return Uri.EscapeDataString(urlSafe);
        }

        public static string GetParam(string videoId, string channelId, int pastSec = 0, bool topchatOnly = false) {
            return Build(videoId, channelId, Times(pastSec), topchatOnly);
        }
    }

    public static class ArcParam {
        private static string Header(string videoId, string channelId) {
            var s1_3 = Encoder.Rs(1, videoId);
            var s1_5 = Encoder.Rs(1, channelId).Concat(Encoder.Rs(2, videoId)).ToArray();
            var s1 = Encoder.Rs(3, s1_3).Concat(Encoder.Rs(5, s1_5)).ToArray();
            var s3 = Encoder.Rs(48687757, Encoder.Rs(1, videoId));
            var headerReplay = Encoder.Rs(1, s1).Concat(Encoder.Rs(3, s3)).Concat(Encoder.Nm(4, 1)).ToArray();
            var base64 = Convert.ToBase64String(headerReplay);
            return base64.Replace("+", "-").Replace("/", "_").TrimEnd('=');
        }

        private static string Build(string videoId, int seektime, bool topchatOnly, string channelId) {
            var chattype = topchatOnly ? 4 : 1;
            if (seektime < 0)
                seektime = 0;
            var timestamp = (long)(seektime * 1000000);
            var header = Encoder.Rs(3, Header(videoId, channelId));
            var timestampField = Encoder.Nm(5, timestamp);
            var s6 = Encoder.Nm(6, 0);
            var s7 = Encoder.Nm(7, 0);
            var s8 = Encoder.Nm(8, 0);
            var s9 = Encoder.Nm(9, 4);
            var s10 = Encoder.Rs(10, Encoder.Nm(4, 0));
            var chattypeField = Encoder.Rs(14, Encoder.Nm(1, 4));
            var s15 = Encoder.Nm(15, 0);
            var entity = header.Concat(timestampField).Concat(s6).Concat(s7).Concat(s8).Concat(s9)
                .Concat(s10).Concat(chattypeField).Concat(s15).ToArray();
            var continuation = Encoder.Rs(156074452, entity);
            var base64 = Convert.ToBase64String(continuation);
            var urlSafe = base64.Replace("+", "-").Replace("/", "_").TrimEnd('=');
            return Uri.EscapeDataString(urlSafe);
        }

        public static string GetParam(string videoId, int seektime = 0, bool topchatOnly = false, string channelId = "") {
            return Build(videoId, seektime, topchatOnly, channelId);
        }
    }

    // Currency symbols mapping
    public static class Currency {
        public static Dictionary<string, Dictionary<string, string>> Symbols = new Dictionary<string, Dictionary<string, string>> {
            ["$"] = new Dictionary<string, string> { ["fxtext"] = "USD", ["jptext"] = "米・ドル" },
            ["A$"] = new Dictionary<string, string> { ["fxtext"] = "AUD", ["jptext"] = "オーストラリア・ドル" },
            ["CA$"] = new Dictionary<string, string> { ["fxtext"] = "CAD", ["jptext"] = "カナダ・ドル" },
            ["CHF\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "CHF", ["jptext"] = "スイス・フラン" },
            ["COP\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "COP", ["jptext"] = "コロンビア・ペソ" },
            ["HK$"] = new Dictionary<string, string> { ["fxtext"] = "HKD", ["jptext"] = "香港・ドル" },
            ["HUF\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "HUF", ["jptext"] = "ハンガリー・フォリント" },
            ["MX$"] = new Dictionary<string, string> { ["fxtext"] = "MXN", ["jptext"] = "メキシコ・ペソ" },
            ["NT$"] = new Dictionary<string, string> { ["fxtext"] = "TWD", ["jptext"] = "台湾・ドル" },
            ["NZ$"] = new Dictionary<string, string> { ["fxtext"] = "NZD", ["jptext"] = "ニュージーランド・ドル" },
            ["PHP\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "PHP", ["jptext"] = "フィリピン・ペソ" },
            ["PLN\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "PLN", ["jptext"] = "ポーランド・ズロチ" },
            ["R$"] = new Dictionary<string, string> { ["fxtext"] = "BRL", ["jptext"] = "ブラジル・レアル" },
            ["RUB\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "RUB", ["jptext"] = "ロシア・ルーブル" },
            ["SEK\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "SEK", ["jptext"] = "スウェーデン・クローナ" },
            ["£"] = new Dictionary<string, string> { ["fxtext"] = "GBP", ["jptext"] = "英・ポンド" },
            ["₩"] = new Dictionary<string, string> { ["fxtext"] = "KRW", ["jptext"] = "韓国・ウォン" },
            ["€"] = new Dictionary<string, string> { ["fxtext"] = "EUR", ["jptext"] = "欧・ユーロ" },
            ["₹"] = new Dictionary<string, string> { ["fxtext"] = "INR", ["jptext"] = "インド・ルピー" },
            ["￥"] = new Dictionary<string, string> { ["fxtext"] = "JPY", ["jptext"] = "日本・円" },
            ["PEN\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "PEN", ["jptext"] = "ペルー・ヌエボ・ソル" },
            ["ARS\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "ARS", ["jptext"] = "アルゼンチン・ペソ" },
            ["CLP\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "CLP", ["jptext"] = "チリ・ペソ" },
            ["NOK\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "NOK", ["jptext"] = "ノルウェー・クローネ" },
            ["BAM\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "BAM", ["jptext"] = "ボスニア・兌換マルカ" },
            ["SGD\u00A0"] = new Dictionary<string, string> { ["fxtext"] = "SGD", ["jptext"] = "シンガポール・ドル" }
        };
    }

    // Parser for YouTube chat JSON
    public class Parser {
        public bool IsReplay { get; set; }

        public (JsonElement contents, string visitorData) GetContents(JsonElement jsn) {
            if (jsn.ValueKind == JsonValueKind.Null)
                throw new InvalidOperationException("Called with null JSON object.");

            if (jsn.TryGetProperty("responseContext", out var responseContext)) {
                if (responseContext.TryGetProperty("errors", out var errors) && errors.ValueKind != JsonValueKind.Null) {
                    var errorText = errors.GetRawText();
                    Console.WriteLine($"API Error: {errorText}");
                    throw new InvalidOperationException($"The video_id would be wrong, or video is deleted or private. Error: {errorText}");
                }
            }

            JsonElement contents = default;
            string visitorData = null;

            // Try both continuationContents and onResponseReceivedActions
            if (jsn.TryGetProperty("continuationContents", out var continuationContents)) {
                contents = continuationContents;
            } else if (jsn.TryGetProperty("onResponseReceivedActions", out var onResponseReceivedActions) && onResponseReceivedActions.ValueKind == JsonValueKind.Array) {
                // Handle onResponseReceivedActions format
                var actionsArray = onResponseReceivedActions.EnumerateArray().ToList();
                if (actionsArray.Count > 0 && actionsArray[0].TryGetProperty("appendContinuationItemsAction", out var appendAction)) {
                    if (appendAction.TryGetProperty("continuationItems", out var continuationItems)) {
                        // Create a wrapper structure
                        contents = continuationItems;
                    }
                }
            }

            if (jsn.TryGetProperty("responseContext", out var rc)) {
                if (rc.TryGetProperty("visitorData", out var vd) && vd.ValueKind == JsonValueKind.String)
                    visitorData = vd.GetString();
            }

            return (contents, visitorData);
        }

        public (Dictionary<string, object> metadata, List<JsonElement> chatdata) Parse(JsonElement contents) {
            if (contents.ValueKind == JsonValueKind.Null)
                throw new InvalidOperationException("Chat data stream is empty.");

            // Handle different response formats
            JsonElement liveChatContinuation;
            if (contents.TryGetProperty("liveChatContinuation", out liveChatContinuation)) {
                // Standard format
            } else if (contents.ValueKind == JsonValueKind.Array) {
                // Array format - might be continuationItems directly
                throw new InvalidOperationException("Unexpected array format in continuation contents.");
            } else {
                Console.WriteLine($"Unexpected contents format. Available properties: {string.Join(", ", contents.EnumerateObject().Select(p => p.Name))}");
                throw new InvalidOperationException("Cannot find liveChatContinuation in response.");
            }

            if (!liveChatContinuation.TryGetProperty("continuations", out var continuations) || continuations.ValueKind != JsonValueKind.Array || continuations.GetArrayLength() == 0) {
                throw new InvalidOperationException("No continuations found in liveChatContinuation.");
            }

            var cont = continuations[0];

            Dictionary<string, object> metadata = null;

            if (cont.TryGetProperty("invalidationContinuationData", out var invalidationData)) {
                metadata = JsonSerializer.Deserialize<Dictionary<string, object>>(invalidationData.GetRawText());
            } else if (cont.TryGetProperty("timedContinuationData", out var timedData)) {
                metadata = JsonSerializer.Deserialize<Dictionary<string, object>>(timedData.GetRawText());
            } else if (cont.TryGetProperty("reloadContinuationData", out var reloadData)) {
                metadata = JsonSerializer.Deserialize<Dictionary<string, object>>(reloadData.GetRawText());
            } else if (cont.TryGetProperty("liveChatReplayContinuationData", out var replayData)) {
                metadata = JsonSerializer.Deserialize<Dictionary<string, object>>(replayData.GetRawText());
            } else if (cont.TryGetProperty("playerSeekContinuationData", out var _)) {
                throw new InvalidOperationException("Finished chat data");
            } else {
                throw new InvalidOperationException("Cannot extract continuation data");
            }

            return CreateData(metadata, contents);
        }

        private (Dictionary<string, object>, List<JsonElement>) CreateData(Dictionary<string, object> metadata, JsonElement contents) {
            var liveChatContinuation = contents.GetProperty("liveChatContinuation");
            List<JsonElement> chatdata;

            if (IsReplay) {
                if (!liveChatContinuation.TryGetProperty("actions", out var actions))
                    actions = default;

                var actionsList = new List<JsonElement>();
                if (actions.ValueKind == JsonValueKind.Array) {
                    foreach (var action in actions.EnumerateArray()) {
                        if (action.TryGetProperty("replayChatItemAction", out var replayAction)) {
                            if (replayAction.TryGetProperty("actions", out var innerActions) && innerActions.ValueKind == JsonValueKind.Array) {
                                if (innerActions.GetArrayLength() > 0)
                                    actionsList.Add(innerActions[0]);
                            }
                        }
                    }
                }

                chatdata = actionsList;
                metadata["timeoutMs"] = 5000L;
                if (actionsList.Count > 0) {
                    var lastAction = actionsList[actionsList.Count - 1];
                    if (lastAction.TryGetProperty("replayChatItemAction", out var lastReplay)) {
                        if (lastReplay.TryGetProperty("videoOffsetTimeMsec", out var offset)) {
                            if (offset.ValueKind == JsonValueKind.Number) {
                                metadata["last_offset_ms"] = offset.GetInt64();
                            } else if (offset.ValueKind == JsonValueKind.String && long.TryParse(offset.GetString(), out var parsedOffset)) {
                                metadata["last_offset_ms"] = parsedOffset;
                            }
                        }
                    }
                }
            } else {
                if (!liveChatContinuation.TryGetProperty("actions", out var actions))
                    actions = default;

                chatdata = actions.ValueKind == JsonValueKind.Array
                    ? actions.EnumerateArray().ToList()
                    : new List<JsonElement>();

                metadata["timeoutMs"] = 5000L;
            }

            return (metadata, chatdata);
        }

        public string ReloadContinuation(JsonElement contents) {
            if (contents.ValueKind == JsonValueKind.Null)
                throw new InvalidOperationException("Chat data stream is empty.");

            var liveChatContinuation = contents.GetProperty("liveChatContinuation");
            var continuations = liveChatContinuation.GetProperty("continuations");
            var cont = continuations[0];

            if (cont.TryGetProperty("liveChatReplayContinuationData", out var _))
                return null;

            if (cont.TryGetProperty("playerSeekContinuationData", out var seekData)) {
                if (seekData.TryGetProperty("continuation", out var continuation))
                    return continuation.GetString();
            }

            throw new InvalidOperationException("Finished chat data");
        }
    }

    // Base renderer
    public abstract class BaseRenderer {
        protected JsonElement Item;
        protected ChatItem Chat;

        public void SetItem(JsonElement item, ChatItem chat) {
            Item = item;
            Chat = chat;
            Chat.Author = new Author();
        }

        public abstract void SetType();

        // Helper method to safely get Int64 from JsonElement (handles both string and number)
        protected long GetInt64Safe(JsonElement element, long defaultValue = 0) {
            if (element.ValueKind == JsonValueKind.Number) {
                return element.GetInt64();
            } else if (element.ValueKind == JsonValueKind.String) {
                var str = element.GetString();
                if (long.TryParse(str, out var parsed)) {
                    return parsed;
                }
            }
            return defaultValue;
        }

        public void GetSnippet() {
            Chat.Id = Item.TryGetProperty("id", out var id) ? id.GetString() : "";

            // Handle timestampUsec which can be either a number or string
            long timestampUsec = 0L;
            if (Item.TryGetProperty("timestampUsec", out var ts)) {
                if (ts.ValueKind == JsonValueKind.Number) {
                    timestampUsec = ts.GetInt64();
                } else if (ts.ValueKind == JsonValueKind.String) {
                    var tsStr = ts.GetString();
                    if (long.TryParse(tsStr, out var parsedTs)) {
                        timestampUsec = parsedTs;
                    }
                }
            }
            Chat.Timestamp = timestampUsec / 1000;

            if (Item.TryGetProperty("timestampText", out var timestampText)) {
                if (timestampText.TryGetProperty("simpleText", out var simpleText))
                    Chat.ElapsedTime = simpleText.GetString();
            } else {
                Chat.ElapsedTime = "";
            }

            Chat.DateTime = GetDateTime(timestampUsec);
            (Chat.Message, Chat.MessageEx) = GetMessage(Item);
            Chat.Id = Item.TryGetProperty("id", out var id2) ? id2.GetString() : "";
            Chat.AmountValue = 0.0;
            Chat.AmountString = "";
            Chat.Currency = "";
            Chat.BgColor = 0;
        }

        public void GetAuthorDetails() {
            Chat.Author.BadgeUrl = "";
            var badges = GetBadges(Item);
            Chat.Author.IsVerified = badges.isVerified;
            Chat.Author.IsChatOwner = badges.isChatOwner;
            Chat.Author.IsChatSponsor = badges.isChatSponsor;
            Chat.Author.IsChatModerator = badges.isChatModerator;

            Chat.Author.ChannelId = Item.TryGetProperty("authorExternalChannelId", out var channelId) ? channelId.GetString() : "";
            Chat.Author.ChannelUrl = $"http://www.youtube.com/channel/{Chat.Author.ChannelId}";
            Chat.Author.Name = Item.TryGetProperty("authorName", out var authorName) && authorName.TryGetProperty("simpleText", out var name) ? name.GetString() : "";

            if (Item.TryGetProperty("authorPhoto", out var authorPhoto) && authorPhoto.TryGetProperty("thumbnails", out var thumbnails)) {
                var thumbnailsArray = thumbnails.EnumerateArray().ToList();
                if (thumbnailsArray.Count > 1)
                    Chat.Author.ImageUrl = thumbnailsArray[1].TryGetProperty("url", out var url) ? url.GetString() : "";
            }
        }

        protected (string message, object messageEx) GetMessage(JsonElement item) {
            var message = "";
            var messageEx = new List<object>();

            if (item.TryGetProperty("message", out var messageObj) && messageObj.TryGetProperty("runs", out var runs)) {
                foreach (var run in runs.EnumerateArray()) {
                    if (run.TryGetProperty("emoji", out var emoji)) {
                        var shortcuts = emoji.TryGetProperty("shortcuts", out var sc) ? sc.EnumerateArray().Select(x => x.GetString()).ToList() : new List<string>();
                        var shortcut = shortcuts.Count > 0 ? shortcuts[0] : "";
                        message += shortcut;

                        if (emoji.TryGetProperty("emojiId", out var emojiId)) {
                            var id = emojiId.GetString().Split('/').LastOrDefault() ?? "";
                            var url = "";
                            if (emoji.TryGetProperty("image", out var image) && image.TryGetProperty("thumbnails", out var emojiThumbnails)) {
                                var emojiThumbs = emojiThumbnails.EnumerateArray().ToList();
                                if (emojiThumbs.Count > 0 && emojiThumbs[0].TryGetProperty("url", out var emojiUrl))
                                    url = emojiUrl.GetString();
                            }

                            messageEx.Add(new Dictionary<string, object> {
                                ["id"] = id,
                                ["txt"] = shortcut,
                                ["url"] = url
                            });
                        }
                    } else if (run.TryGetProperty("text", out var text)) {
                        var textValue = text.GetString();
                        message += textValue;
                        messageEx.Add(textValue);
                    }
                }
            }

            return (message, messageEx);
        }

        protected (bool isVerified, bool isChatOwner, bool isChatSponsor, bool isChatModerator) GetBadges(JsonElement renderer) {
            bool isVerified = false, isChatOwner = false, isChatSponsor = false, isChatModerator = false;

            if (renderer.TryGetProperty("authorBadges", out var authorBadges)) {
                foreach (var badge in authorBadges.EnumerateArray()) {
                    if (badge.TryGetProperty("liveChatAuthorBadgeRenderer", out var badgeRenderer)) {
                        if (badgeRenderer.TryGetProperty("icon", out var icon) && icon.TryGetProperty("iconType", out var iconType)) {
                            var authorType = iconType.GetString();
                            if (authorType == "VERIFIED")
                                isVerified = true;
                            else if (authorType == "OWNER")
                                isChatOwner = true;
                            else if (authorType == "MODERATOR")
                                isChatModerator = true;
                        }

                        if (badgeRenderer.TryGetProperty("customThumbnail", out var _)) {
                            isChatSponsor = true;
                            if (badgeRenderer.TryGetProperty("customThumbnail", out var customThumbnail) && customThumbnail.TryGetProperty("thumbnails", out var thumbnails)) {
                                var thumbs = thumbnails.EnumerateArray().ToList();
                                if (thumbs.Count > 0 && thumbs[0].TryGetProperty("url", out var badgeUrl))
                                    Chat.Author.BadgeUrl = badgeUrl.GetString();
                            }
                        }
                    }
                }
            }

            return (isVerified, isChatOwner, isChatSponsor, isChatModerator);
        }

        protected string GetDateTime(long timestamp) {
            var dt = DateTimeOffset.FromUnixTimeMilliseconds(timestamp / 1000).DateTime;
            return dt.ToString("yyyy-MM-dd HH:mm:ss");
        }

        public ChatItem GetChatObj() {
            return Chat;
        }

        public void Clear() {
            Item = default;
            Chat = null;
        }
    }

    // Specific renderers
    public class LiveChatTextMessageRenderer : BaseRenderer {
        public override void SetType() {
            Chat.Type = "textMessage";
        }
    }

    public class LiveChatPaidMessageRenderer : BaseRenderer {
        private static readonly Regex SuperchatRegex = new Regex(@"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$", RegexOptions.Compiled);

        public override void SetType() {
            Chat.Type = "superChat";
        }

        public new void GetSnippet() {
            base.GetSnippet();
            var (amountDisplayString, symbol, amount) = GetAmountData(Item);
            Chat.AmountValue = amount;
            Chat.AmountString = amountDisplayString;
            Chat.Currency = Currency.Symbols.ContainsKey(symbol) ? Currency.Symbols[symbol]["fxtext"] : symbol;
            Chat.BgColor = Item.TryGetProperty("bodyBackgroundColor", out var bgColor) ? GetInt64Safe(bgColor) : 0;
            Chat.Colors = GetColors();
        }

        private (string amountDisplayString, string symbol, double amount) GetAmountData(JsonElement item) {
            if (!item.TryGetProperty("purchaseAmountText", out var purchaseAmountText) || !purchaseAmountText.TryGetProperty("simpleText", out var simpleText))
                return ("", "", 0.0);

            var amountDisplayString = simpleText.GetString();
            var match = SuperchatRegex.Match(amountDisplayString);
            if (match.Success) {
                var symbol = match.Groups[1].Value;
                var amountStr = match.Groups[2].Value.Replace(",", "");
                if (double.TryParse(amountStr, out var amount))
                    return (amountDisplayString, symbol, amount);
            }

            return (amountDisplayString, "", 0.0);
        }

        private Colors GetColors() {
            var colors = new Colors();
            colors.HeaderBackgroundColor = Item.TryGetProperty("headerBackgroundColor", out var hbg) ? GetInt64Safe(hbg) : 0;
            colors.HeaderTextColor = Item.TryGetProperty("headerTextColor", out var htc) ? GetInt64Safe(htc) : 0;
            colors.BodyBackgroundColor = Item.TryGetProperty("bodyBackgroundColor", out var bbg) ? GetInt64Safe(bbg) : 0;
            colors.BodyTextColor = Item.TryGetProperty("bodyTextColor", out var btc) ? GetInt64Safe(btc) : 0;
            colors.TimestampColor = Item.TryGetProperty("timestampColor", out var tc) ? GetInt64Safe(tc) : 0;
            colors.AuthorNameTextColor = Item.TryGetProperty("authorNameTextColor", out var antc) ? GetInt64Safe(antc) : 0;
            return colors;
        }
    }

    public class LiveChatPaidStickerRenderer : BaseRenderer {
        private static readonly Regex SuperchatRegex = new Regex(@"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$", RegexOptions.Compiled);

        public override void SetType() {
            Chat.Type = "superSticker";
        }

        public new void GetSnippet() {
            base.GetSnippet();
            var (amountDisplayString, symbol, amount) = GetAmountData(Item);
            Chat.AmountValue = amount;
            Chat.AmountString = amountDisplayString;
            Chat.Currency = Currency.Symbols.ContainsKey(symbol) ? Currency.Symbols[symbol]["fxtext"] : symbol;
            Chat.BgColor = Item.TryGetProperty("backgroundColor", out var bgColor) ? GetInt64Safe(bgColor) : 0;

            if (Item.TryGetProperty("sticker", out var sticker) && sticker.TryGetProperty("thumbnails", out var thumbnails)) {
                var thumbs = thumbnails.EnumerateArray().ToList();
                if (thumbs.Count > 0 && thumbs[0].TryGetProperty("url", out var url))
                    Chat.Sticker = "https:" + url.GetString();
            }

            Chat.Colors = GetColors();
        }

        private (string amountDisplayString, string symbol, double amount) GetAmountData(JsonElement item) {
            if (!item.TryGetProperty("purchaseAmountText", out var purchaseAmountText) || !purchaseAmountText.TryGetProperty("simpleText", out var simpleText))
                return ("", "", 0.0);

            var amountDisplayString = simpleText.GetString();
            var match = SuperchatRegex.Match(amountDisplayString);
            if (match.Success) {
                var symbol = match.Groups[1].Value;
                var amountStr = match.Groups[2].Value.Replace(",", "");
                if (double.TryParse(amountStr, out var amount))
                    return (amountDisplayString, symbol, amount);
            }

            return (amountDisplayString, "", 0.0);
        }

        private Colors GetColors() {
            var colors = new Colors();
            colors.MoneyChipBackgroundColor = Item.TryGetProperty("moneyChipBackgroundColor", out var mcbg) ? GetInt64Safe(mcbg) : 0;
            colors.MoneyChipTextColor = Item.TryGetProperty("moneyChipTextColor", out var mctc) ? GetInt64Safe(mctc) : 0;
            colors.BackgroundColor = Item.TryGetProperty("backgroundColor", out var bg) ? GetInt64Safe(bg) : 0;
            colors.AuthorNameTextColor = Item.TryGetProperty("authorNameTextColor", out var antc) ? GetInt64Safe(antc) : 0;
            return colors;
        }
    }

    public class LiveChatLegacyPaidMessageRenderer : BaseRenderer {
        public override void SetType() {
            Chat.Type = "superChat";
        }
    }

    public class LiveChatMembershipItemRenderer : BaseRenderer {
        public override void SetType() {
            Chat.Type = "newSponsor";
        }

        public new void GetAuthorDetails() {
            base.GetAuthorDetails();
            Chat.Author.IsChatSponsor = true;
        }

        protected new (string message, object messageEx) GetMessage(JsonElement item) {
            try {
                if (item.TryGetProperty("headerSubtext", out var headerSubtext) && headerSubtext.TryGetProperty("runs", out var runs)) {
                    var message = "";
                    var messageEx = new List<object>();
                    foreach (var run in runs.EnumerateArray()) {
                        if (run.TryGetProperty("text", out var text)) {
                            var textValue = text.GetString();
                            message += textValue;
                            messageEx.Add(textValue);
                        }
                    }
                    return (message, messageEx);
                }
            } catch { }

            return ("Welcome New Member!", new List<object> { "Welcome New Member!" });
        }
    }

    public class LiveChatDonationAnnouncementRenderer : BaseRenderer {
        public override void SetType() {
            Chat.Type = "superChat";
        }
    }

    // Default Processor
    public class DefaultProcessor {
        private bool first = true;
        private double absDiff = 0;
        private readonly Dictionary<string, BaseRenderer> renderers;

        public DefaultProcessor() {
            renderers = new Dictionary<string, BaseRenderer> {
                ["liveChatTextMessageRenderer"] = new LiveChatTextMessageRenderer(),
                ["liveChatPaidMessageRenderer"] = new LiveChatPaidMessageRenderer(),
                ["liveChatPaidStickerRenderer"] = new LiveChatPaidStickerRenderer(),
                ["liveChatLegacyPaidMessageRenderer"] = new LiveChatLegacyPaidMessageRenderer(),
                ["liveChatMembershipItemRenderer"] = new LiveChatMembershipItemRenderer(),
                ["liveChatDonationAnnouncementRenderer"] = new LiveChatDonationAnnouncementRenderer()
            };
        }

        public ChatData Process(List<Dictionary<string, object>> chatComponents) {
            var chatlist = new List<ChatItem>();
            double timeout = 0;

            if (chatComponents != null) {
                foreach (var component in chatComponents) {
                    if (component == null)
                        continue;

                    if (component.TryGetValue("timeout", out var timeoutObj)) {
                        if (timeoutObj is double t)
                            timeout += t;
                        else if (timeoutObj is int ti)
                            timeout += ti;
                    }

                    if (!component.TryGetValue("chatdata", out var chatdataObj) || chatdataObj == null)
                        continue;

                    if (chatdataObj is List<JsonElement> chatdata) {
                        foreach (var action in chatdata) {
                            if (action.ValueKind == JsonValueKind.Null)
                                continue;

                            if (!action.TryGetProperty("addChatItemAction", out var addChatItemAction))
                                continue;

                            if (!addChatItemAction.TryGetProperty("item", out var item))
                                continue;

                            var chat = Parse(item);
                            if (chat != null)
                                chatlist.Add(chat);
                        }
                    }
                }
            }

            if (first && chatlist.Count > 0) {
                absDiff = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() - chatlist[0].Timestamp;
                first = false;
            }

            return new ChatData {
                Items = chatlist,
                Interval = timeout,
                AbsDiff = absDiff
            };
        }

        private ChatItem Parse(JsonElement item) {
            try {
                var properties = item.EnumerateObject().ToList();
                if (properties.Count == 0) {
                    Console.WriteLine("Parse: item has no properties");
                    return null;
                }

                var key = properties[0].Name;

                // Skip non-chat message types
                var skipTypes = new HashSet<string> {
                    "liveChatViewerEngagementMessageRenderer",
                    "liveChatPlaceholderItemRenderer"
                };

                if (skipTypes.Contains(key)) {
                    // Silently skip viewer engagement and placeholder messages
                    return null;
                }

                if (!renderers.TryGetValue(key, out var renderer)) {
                    // Only log if it's not a known skip type
                    Console.WriteLine($"Parse: Unknown renderer type '{key}' - skipping. Available renderers: {string.Join(", ", renderers.Keys)}");
                    return null;
                }

                var chat = new ChatItem();
                renderer.SetItem(properties[0].Value, chat);
                renderer.SetType();
                renderer.GetSnippet();
                renderer.GetAuthorDetails();
                var chatObj = renderer.GetChatObj();
                renderer.Clear();
                return chatObj;
            } catch (Exception ex) {
                Console.WriteLine($"Parse: Exception occurred: {ex.Message}");
                Console.WriteLine($"Parse: Stack trace: {ex.StackTrace}");
                return null;
            }
        }
    }

    // Main PytchatCore class
    public class PytchatCore : IDisposable {
        private readonly HttpClient _client;
        private readonly string _videoId;
        private readonly int _seektime;
        private readonly DefaultProcessor _processor;
        private bool _isAlive = true;
        private bool _isReplay;
        private readonly Parser _parser;
        private bool _firstFetch;
        private string _fetchUrl;
        private readonly bool _topchatOnly;
        private string _dat = "";
        private int _lastOffsetMs = 0;
        private string _continuation;
        private const int MaxRetry = 10;
        private const string LiveUrl = "https://www.youtube.com/youtubei/v1/live_chat/get_live_chat";
        private const string ReplayUrl = "https://www.youtube.com/youtubei/v1/live_chat/get_live_chat_replay";

        public PytchatCore(string videoId, int seektime = -1, bool forceReplay = false, bool topchatOnly = false, string replayContinuation = null) {
            _videoId = Utils.ExtractVideoId(videoId);
            _seektime = seektime;
            _processor = new DefaultProcessor();
            _isReplay = forceReplay || replayContinuation != null;
            _parser = new Parser { IsReplay = _isReplay };
            _firstFetch = replayContinuation == null;
            _fetchUrl = replayContinuation == null ? LiveUrl : ReplayUrl;
            _topchatOnly = topchatOnly;
            _continuation = replayContinuation;

            _client = new HttpClient();
            _client.DefaultRequestHeaders.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63");

            _setupTask = SetupAsync();
        }

        private Task _setupTask;

        private async Task SetupAsync() {
            if (_continuation == null) {
                await Task.Delay(100);
                var channelId = await Utils.GetChannelIdAsync(_client, _videoId);
                _continuation = LiveParam.GetParam(_videoId, channelId, pastSec: 3);
            }
        }

        public async Task<ChatData> GetAsync() {
            if (_setupTask != null && !_setupTask.IsCompleted)
                await _setupTask;

            if (!IsAlive())
                return new ChatData();

            var chatComponent = await GetChatComponentAsync();
            if (chatComponent == null)
                return new ChatData();

            return _processor.Process(new List<Dictionary<string, object>> { chatComponent });
        }

        private async Task<Dictionary<string, object>> GetChatComponentAsync() {
            try {
                if (_continuation != null && _isAlive) {
                    var contents = await GetContentsAsync(_continuation);
                    if (contents.contents.ValueKind == JsonValueKind.Null)
                        return null;

                    var (metadata, chatdata) = _parser.Parse(contents.contents);
                    double timeout = 5.0;
                    if (metadata.ContainsKey("timeoutMs")) {
                        if (metadata["timeoutMs"] is JsonElement je) {
                            if (je.ValueKind == JsonValueKind.Number) {
                                timeout = je.GetInt64() / 1000.0;
                            } else if (je.ValueKind == JsonValueKind.String && long.TryParse(je.GetString(), out var parsedTimeout)) {
                                timeout = parsedTimeout / 1000.0;
                            }
                        } else if (metadata["timeoutMs"] is long l)
                            timeout = l / 1000.0;
                        else if (metadata["timeoutMs"] is int i)
                            timeout = i / 1000.0;
                    }

                    if (contents.visitorData != null)
                        _dat = contents.visitorData;

                    _continuation = null;
                    if (metadata.ContainsKey("continuation")) {
                        if (metadata["continuation"] is JsonElement contJe && contJe.ValueKind == JsonValueKind.String)
                            _continuation = contJe.GetString();
                        else if (metadata["continuation"] is string contStr)
                            _continuation = contStr;
                    }

                    if (metadata.ContainsKey("last_offset_ms")) {
                        if (metadata["last_offset_ms"] is JsonElement offsetJe) {
                            if (offsetJe.ValueKind == JsonValueKind.Number) {
                                _lastOffsetMs = (int)offsetJe.GetInt64();
                            } else if (offsetJe.ValueKind == JsonValueKind.String && long.TryParse(offsetJe.GetString(), out var parsedOffset)) {
                                _lastOffsetMs = (int)parsedOffset;
                            }
                        } else if (metadata["last_offset_ms"] is long offsetL)
                            _lastOffsetMs = (int)offsetL;
                        else if (metadata["last_offset_ms"] is int offsetI)
                            _lastOffsetMs = offsetI;
                    }

                    var chatComponent = new Dictionary<string, object> {
                        ["video_id"] = _videoId,
                        ["timeout"] = timeout,
                        ["chatdata"] = chatdata
                    };

                    return chatComponent;
                }
            } catch (Exception ex) {
                Console.WriteLine($"Error in GetChatComponentAsync: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
                Terminate();
            }

            return null;
        }

        private async Task<(JsonElement contents, string visitorData)> GetContentsAsync(string continuation) {
            JsonElement livechatJson = default;
            Exception lastError = null;

            if (_lastOffsetMs < 0)
                _lastOffsetMs = 0;

            var param = Utils.GetParam(continuation, replay: _isReplay, offsetMs: _lastOffsetMs, dat: _dat);
            var jsonOptions = new JsonSerializerOptions {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };

            for (int i = 0; i <= MaxRetry; i++) {
                try {
                    var jsonContent = JsonSerializer.Serialize(param, jsonOptions);
                    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
                    var response = await _client.PostAsync(_fetchUrl, content);
                    var responseText = await response.Content.ReadAsStringAsync();

                    if (!response.IsSuccessStatusCode) {
                        Console.WriteLine($"HTTP Error: {response.StatusCode} - {responseText}");
                        lastError = new HttpRequestException($"HTTP {response.StatusCode}: {responseText}");
                        if (i < MaxRetry) {
                            await Task.Delay(2000);
                            continue;
                        }
                        break;
                    }

                    livechatJson = JsonSerializer.Deserialize<JsonElement>(responseText);
                    break;
                } catch (Exception ex) {
                    lastError = ex;
                    Console.WriteLine($"Request error (attempt {i + 1}/{MaxRetry + 1}): {ex.Message}");
                    if (i < MaxRetry)
                        await Task.Delay(2000);
                }
            }

            if (livechatJson.ValueKind == JsonValueKind.Null) {
                throw new InvalidOperationException($"Exceeded retry count. Last error: {lastError?.Message}");
            }

            var (contents, visitorData) = _parser.GetContents(livechatJson);

            if (_firstFetch) {
                if (contents.ValueKind == JsonValueKind.Null || _isReplay) {
                    _parser.IsReplay = true;
                    _fetchUrl = ReplayUrl;
                    var channelId = await Utils.GetChannelIdAsync(_client, _videoId);
                    continuation = ArcParam.GetParam(_videoId, _seektime, _topchatOnly, channelId);
                    livechatJson = await GetLivechatJsonAsync(continuation, replay: true, offsetMs: _seektime * 1000);
                    (contents, _) = _parser.GetContents(livechatJson);

                    var reloadContinuation = _parser.ReloadContinuation(contents);
                    if (reloadContinuation != null) {
                        livechatJson = await GetLivechatJsonAsync(reloadContinuation, replay: true);
                        (contents, _) = _parser.GetContents(livechatJson);
                    }

                    _isReplay = true;
                }
                _firstFetch = false;
            }

            return (contents, visitorData);
        }

        private async Task<JsonElement> GetLivechatJsonAsync(string continuation, bool replay = false, int offsetMs = 0) {
            if (offsetMs < 0)
                offsetMs = 0;

            var param = Utils.GetParam(continuation, replay: replay, offsetMs: offsetMs, dat: _dat);
            var jsonOptions = new JsonSerializerOptions {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };

            for (int i = 0; i <= MaxRetry; i++) {
                try {
                    var jsonContent = JsonSerializer.Serialize(param, jsonOptions);
                    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
                    var response = await _client.PostAsync(_fetchUrl, content);
                    var responseText = await response.Content.ReadAsStringAsync();

                    if (!response.IsSuccessStatusCode) {
                        Console.WriteLine($"HTTP Error in GetLivechatJsonAsync: {response.StatusCode} - {responseText}");
                        if (i < MaxRetry) {
                            await Task.Delay(2000);
                            continue;
                        }
                        throw new HttpRequestException($"HTTP {response.StatusCode}: {responseText}");
                    }


                    return JsonSerializer.Deserialize<JsonElement>(responseText);
                } catch (Exception ex) {
                    Console.WriteLine($"GetLivechatJsonAsync error (attempt {i + 1}/{MaxRetry + 1}): {ex.Message}");
                    if (i < MaxRetry)
                        await Task.Delay(2000);
                    else
                        throw;
                }
            }

            return default;
        }

        public bool IsReplay() {
            return _isReplay;
        }

        public bool IsAlive() {
            return _isAlive;
        }

        public void Terminate() {
            if (!IsAlive())
                return;
            _isAlive = false;
        }

        public void Dispose() {
            _client?.Dispose();
        }
    }

    // Factory method matching Python's create() function
    public static class Pytchat {
        public static PytchatCore Create(string videoId, int seektime = -1, bool forceReplay = false, bool topchatOnly = false, string replayContinuation = null) {
            return new PytchatCore(videoId, seektime, forceReplay, topchatOnly, replayContinuation);
        }
    }
}
