package teaType.util.statics;

import teaType.util.Array;

public class Randomizer extends Random {
	private static final long serialVersionUID = 1L, PHI = 0x9E3779B97F4A7C15L;
	private long x;

	public static double random() {
		return new Random().nextDouble();
	}

	public Randomizer() {
		this(System.nanoTime());
	}

	public Randomizer(final long seed) {
		x = seed;
	}

	public static int[] generateInteger(int n, int bound, boolean pos, boolean sort, boolean asc) {
		Randomizer r = new Randomizer();
		int[] arr = new int[n];
		int[] temp;
		for(int i = 0; i < n; i++) {
			if(bound != 0) {
				arr[i] = r.nextInt(bound);
			} else {
				arr[i] = r.nextInt();	
			}
		}

		if(pos) {
			temp = new int[arr.length];
			for(int i = 0; i++ < arr.length; i++) {
				temp[i] = Math.abs(arr[i]);
			}
			arr = temp;
			temp = null;
		}

		if(sort) {
			Array.dualPivotSort(arr, asc);
		}
		return arr;
	}

	public static long[] generateLong(int n) {
		return new long[10];
	}

	public static double[] generateDouble(int n) {
		return new double[10];
	}

	public static String[] generateString(int n) {
		return new String[10];
	}

	private static long staffordMix13(long z) {
		z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
		z = (z ^ (z >>> 27)) * 0x94D049BB133111EBL;
		return z ^ (z >>> 31);
	}

	private static int staffordMix4Upper32(long z) {
		z = (z ^ (z >>> 33)) * 0x62A9D9ED799705F5L;
		return (int) (((z ^ (z >>> 28)) * 0xCB24D0A5C88C35B3L) >>> 32);
	}

	public long nextLong() {
		return staffordMix13(x += PHI);
	}

	public int nextInt() {
		return staffordMix4Upper32(x += PHI);
	}

	public int nextInt(final int n) {
		return (int)nextLong(n);
	}

	public long nextLong(final long n) {
		if (n <= 0) {
			throw new IllegalArgumentException("illegal bound " + n + " (must be positive)");
		}
		long t = staffordMix13(x += PHI);
		final long nMinus1 = n - 1;
		if ((n & nMinus1) == 0) {
			return t & nMinus1;
		}
		for (long u = t >>> 1; u + nMinus1 - (t = u % n) < 0;
				u = staffordMix13(x += PHI) >>> 1);
		return t;
	}

	public double nextDouble() {
		return Double.longBitsToDouble(staffordMix13(x += PHI) >>> 12 | 0x3FFL << 52) - 1.0;
	}

	public float nextFloat() {
		return Float.intBitsToFloat(staffordMix4Upper32(x += PHI) >>> 41 | 0x3F8 << 20) - 1.0f;
	}

	public boolean nextBoolean() {
		return staffordMix4Upper32(x += PHI) < 0;
	}

	public void nextBytes(final byte[] bytes) {
		int i = bytes.length, n = 0;
		while (i != 0) {
			n = Math.min(i, 8);
			for (long bits = staffordMix13(x += PHI); n-- != 0; bits >>= 8) {
				bytes[--i] = (byte)bits;
			}
		}
	}
}