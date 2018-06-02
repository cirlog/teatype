package teaType.util;

import java.io.PrintWriter;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * 
 * @author Burak Günaydin
 */

public class Array {
	final static PrintWriter out = new PrintWriter(System.out, true);

	public static final void print(String[] arr, boolean linebreak, boolean whitespace) {
		for(String s : arr) {
			if(linebreak) {
				out.println(s);
			} else {
				if(whitespace) {
					out.print(s + " ");	
				} else {
					out.print(s);
				}
			}
		}
		out.flush();
		out.println();
	}

	public static final void print(int[] arr, boolean linebreak, boolean whitespace) {
		for(int i : arr) {
			if(linebreak) {
				out.println(i);
			} else {
				if(whitespace) {
					out.print(i + " ");	
				} else {
					out.print(i);
				}
			}
		}
		out.flush();
		out.println();
	}

	/* TEMPORARY SOLUTION FOR ALLROUND-METHOD */
	public static int[] add(int[] arr, int i) {
		int[] temp = new int[arr.length+1];
		for(int c = 0; c < arr.length; c++) {
			temp[c] = arr[c];
		}
		temp[arr.length] = i;
		return temp;
	}

	public static int[] remove(int[] arr, int index) {
		int[] temp = new int[arr.length-1];
		for(int i = 0; i < arr.length; i++) {
			if(i == index) {
				continue;
			}
			temp[i] = arr[i];
		}
		return temp;
	}
	/* -------------------------------------- */

	public static <T> T[] add(T[] arr, T t) {
		@SuppressWarnings("unchecked")
		T[] temp = (T[]) java.lang.reflect.Array.newInstance(arr.getClass().getComponentType(), arr.length+1);
		for(int i = 0; i < arr.length; i++) {
			temp[i] = arr[i];
		}
		temp[arr.length] = t;
		return temp;
	}

	public static <T> T[] remove(T[] arr, int index) {
		@SuppressWarnings("unchecked")
		T[] temp = (T[]) java.lang.reflect.Array.newInstance(arr.getClass().getComponentType(), arr.length-1);
		for(int i = 0; i < arr.length; i++) {
			if(i == index) {
				continue;
			}
			temp[i] = arr[i];
		}
		return temp;
	}

	/* Adapted from Apache Commons Lang 3-3.5 */
	public static <T> T[] clone(final T[] array) {
		if (array == null) {
			return null;
		}
		return array.clone();
	}

	/* Adapted from Apache Commons Lang 3-3.5 */
	@SafeVarargs
	public static <T> T[] fuse(T[] main, T... join) {
		if(main == null) {
			return clone(join);
		} else if(join == null) {
			return clone(main);
		}
		Class<?> type = main.getClass().getComponentType();
		@SuppressWarnings("unchecked")
		T[] arr = (T[]) java.lang.reflect.Array.newInstance(type, main.length + join.length);
		System.arraycopy(main, 0, arr, 0, main.length);
		try {
			System.arraycopy(join, 0, arr, main.length, join.length);
		} catch (ArrayStoreException e) {
			e.printStackTrace();
		}
		return arr;
	}

	public final static ArrayList<String> toArrayList(String[] arr) {
		ArrayList<String> temp = new ArrayList<String>();
		for(int i = 0; i < arr.length; i++) {
			temp.add(arr[i]);
		}
		return temp;
	}

	public final static ArrayList<Integer> toArrayList(int[] arr) {
		ArrayList<Integer> temp = new ArrayList<Integer>();
		for(int i = 0; i < arr.length; i++) {
			temp.add(arr[i]);
		}
		return temp;
	}

	public final static ArrayList<Double> toArrayList(double[] arr) {
		ArrayList<Double> temp = new ArrayList<Double>();
		for(int i = 0; i < arr.length; i++) {
			temp.add(arr[i]);
		}
		return temp;
	}

	public final static <T> ArrayList<T> toArrayList(T[] arr) {
		Class<?> type = arr.getClass().getComponentType();
		@SuppressWarnings("unchecked")
		T[] foo = (T[]) java.lang.reflect.Array.newInstance(type, arr.length);
		ArrayList<T> temp = new ArrayList<T>();
		for(int i = 0; i < arr.length; i++) {
			temp.add(foo[i]);
		}
		return temp;
	}

	public final static String[] fromArrayList(ArrayList<String> list) {
		String[] temp = new String[list.size()];
		for (int i = 0; i < list.size(); i++) {
			temp[i] = list.get(i);
		}
		return temp;
	}

	/*
	public final static int[] fromArrayList(ArrayList<Integer> list) {
		int[] temp = new int[list.size()];
		for (int i = 0; i < list.size(); i++) {
			temp[i] = list.get(i);
		}
		return temp;
	}

	public final static double[] fromArrayList(ArrayList<Double> list) {
		double[] temp = new double[list.size()];
		for (int i = 0; i < list.size(); i++) {
			temp[i] = list.get(i);
		}
		return temp;
	}
	 */
	
	public final static void sort(String[] arr, boolean asc) {
		String[] temp = new String[arr.length];
		for(int i = 0; i < temp.length; i++) {
			temp[i] = null;
		}
		arr = temp;
	}

	final static void sortDescending(int[] arr) {
		int[] temp = new int[arr.length];
		for(int i = 0; i < temp.length; i++) {
			temp[i] = arr[arr.length-i-1];
		}
		arr = temp;
	}

	public static void quicksort(int[] arr, boolean asc) {
		qS(arr, 0, arr.length-1);
		if(!asc) {
			sortDescending(arr);
		}
	}

	private static void qS(int[] arr, int left, int right) {
		int pivot = arr[(left + right) >> 1];
		int l = left;
		int r = right;
		while(l <= r) {
			while(arr[l] < pivot) {
				l++;
			}
			while(arr[r] > pivot) {
				r--;
			}
			if(l <= r) {
				swap(arr, l++, r--);
			}
		}
		if(left < r) {
			qS(arr, left, r);
		}
		if(l < right) {
			qS(arr, l, right);
		}
	}

	final static void swap(int[] arr, int left, int right) {
		int temp = arr[left];
		arr[left] = arr[right];
		arr[right] = temp;
	}

	public static void dualPivotSort(int[] arr, boolean asc) {
		Arrays.sort(arr);
		if(!asc) {
			sortDescending(arr);
		}
	}

	public static void mergesort(int[] arr, boolean asc) {
		mS(0, arr.length-1, arr, new int[(arr.length+1) / 2]);
		if(!asc) {
			sortDescending(arr);
		}
	}

	final static void mS(int l, int r, int[] arr, int[] temp) {
		if(l < r) {
			int m = l + (r - l) / 2;
			mS(l, m, arr, temp);
			mS(m + 1, r, arr, temp);
			m(l, m, r, arr, temp);
		}
	}

	final static void m(int l, int m, int r, int[] arr, int[] temp) {
		int iOfA1 = 0;
		int iOfA2 = l;
		int index = l;
		while(iOfA2 <= m) {
			temp[iOfA1] = arr[iOfA2];
			iOfA1++;
			iOfA2++;
		}

		iOfA1 = 0;
		while(index<iOfA2 && iOfA2<=r) {
			if(temp[iOfA1] <= arr[iOfA2]) {
				arr[index] = temp[iOfA1];
				iOfA1++;
			} else {
				arr[index] = arr[iOfA2];
				iOfA2++;
			}
			index++;
		}

		while(index<iOfA2) {
			arr[index] = temp[iOfA1];
			index++;
			iOfA1++;
		}
	}
}