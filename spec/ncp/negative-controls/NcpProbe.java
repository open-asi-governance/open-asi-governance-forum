import java.lang.reflect.Method;

/** NEGATIVE CONTROL driver for a component-health aggregator.
 *
 *  Calls a static, no-argument method that returns an aggregated health object, and prints what
 *  it returned. Run it repeatedly with different -D flags to see which configurations change the
 *  aggregate verdict and which change only a nested field.
 *
 *  Reflective on purpose: the technique is "drive the aggregator directly rather than through the
 *  HTTP surface, so a stale build cannot be mistaken for a fixed one". Naming a particular class
 *  would tie the technique to one codebase.
 *
 *  Usage:
 *    java -cp "<app-jar>:<deps>" -D<flag>=<value> NcpProbe.java com.example.Health getHealthStatus
 */
public class NcpProbe {
  public static void main(String[] args) throws Exception {
    if (args.length < 2) {
      System.err.println("usage: NcpProbe <fully.qualified.Class> <staticNoArgMethod>");
      System.exit(2);
    }
    final Method method = Class.forName(args[0]).getMethod(args[1]);
    final Object result = method.invoke(null);
    System.out.println("RESULT=" + result);
  }
}
