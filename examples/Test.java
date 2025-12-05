public class Test {
    public static void main(String[] args) {
        int a = 10;
        int b = 0;
        // Intentional divide by zero for analysis
        System.out.println(divide(a, b));
    }

    public static int divide(int a, int b) {
        return a / b;
    }
}
