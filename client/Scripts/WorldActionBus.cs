using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public class WorldAction {
    public string type;
    public Dictionary<string, string> paramsDict;
}

public class WorldActionBus : MonoBehaviour
{
    public GameObject doorPrefab;
    public GameObject nodePrefab;
    public GameObject dronePrefab;

    public void Apply(List<WorldAction> actions)
    {
        foreach (var act in actions)
        {
            switch (act.type)
            {
                case "open_door":
                    if (act.paramsDict != null && act.paramsDict.ContainsKey("id"))
                        OpenDoor(act.paramsDict["id"]);
                    else OpenDoor("D-01");
                    break;
                case "animate_nodes":
                    AnimateNodes(act.paramsDict);
                    break;
                case "drone_fall":
                    if (act.paramsDict != null && act.paramsDict.ContainsKey("id"))
                        DroneFall(act.paramsDict["id"]);
                    else DroneFall("DR-01");
                    break;
                default:
                    Debug.LogWarning("Unknown action: " + act.type);
                    break;
            }
        }
    }

    private void OpenDoor(string id)
    {
        Debug.Log("Opening door " + id);
        // TODO: trigger door animation, sound, VFX
    }

    private void AnimateNodes(Dictionary<string, string> args)
    {
        Debug.Log("Animating nodes...");
        // TODO: animate nodes based on args["enabled"] / args["skipped"]
    }

    private void DroneFall(string id)
    {
        Debug.Log("Drone " + id + " falling");
        // TODO: play fall animation
    }
}
