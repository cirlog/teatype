package teaType._debug.commonTests;

public class IntToDoubleConversion {
	public static void main(String[] args) {
		double base = 0.0;
		int max = 512;
		int arm = 150;
		double temp = (double) arm/max;
		base+= temp;
		System.out.println(base);
	}
}