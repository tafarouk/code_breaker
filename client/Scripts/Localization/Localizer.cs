using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class Localizer : MonoBehaviour
{
    public static Localizer I;
    public string language = "en";
    private Dictionary<string, string> primary;
    private Dictionary<string, string> fallback;

    void Awake()
    {
        if (I == null) I = this; else Destroy(gameObject);
        DontDestroyOnLoad(gameObject);
        primary = LoadPack(language);
        fallback = language == "en" ? primary : LoadPack("en");
        ApplyRTLFlag();
    }

    private Dictionary<string, string> LoadPack(string lang)
    {
        var path = Path.Combine(Application.streamingAssetsPath, "i18n", lang + ".json");
        var json = File.ReadAllText(path);
        // NOTE: In a real project, use Newtonsoft JSON for Unity and parse into Dictionary<string,string>
        var dict = new Dictionary<string, string>(); // placeholder for demo
        dict["meta.lang"] = lang;
        dict["meta.rtl"] = (lang == "ar") ? "true" : "false";
        return dict;
    }

    public string T(string key, Dictionary<string, object> vars = null)
    {
        string s = null;
        if (primary != null && primary.TryGetValue(key, out s) == false) s = null;
        if (s == null && fallback != null && fallback.TryGetValue(key, out s) == false) s = key;
        if (vars != null)
            foreach (var kv in vars)
                s = s.Replace("{" + kv.Key + "}", kv.Value.ToString());
        return s;
    }

    public bool IsRTL() => primary.ContainsKey("meta.rtl") && primary["meta.rtl"] == "true";

    private void ApplyRTLFlag()
    {
        // Hook layout direction flip here if IsRTL()
    }
}
