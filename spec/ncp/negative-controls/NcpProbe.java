import com.consullo.util.SystemUtilities;
import org.json.simple.JSONObject;

/** NEGATIVE CONTROLS for the health endpoint's own checks. Drives the real getHealthStatus(). */
public class NcpProbe {
  public static void main(String[] a) throws Exception {
    JSONObject h = SystemUtilities.getHealthStatus();
    System.out.println("STATUS=" + h.get("status"));
    System.out.println("BODY=" + h.toJSONString());
  }
}
