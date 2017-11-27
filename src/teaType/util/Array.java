package teaType.util;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * 
 * @author Burak Günaydin
 */

public class Array {
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
	
	public static <T> T[] clone(final T[] array) {
		if (array == null) {
			return null;
		}
		return array.clone();
	}
	
	@SafeVarargs
	public static <T> T[] fuse(T[] mainArr, T... joinArr) {
		if(mainArr == null) {
			return clone(joinArr);
		} else if (joinArr == null) {
			return clone(mainArr);
		}
		Class<?> arrType1 = mainArr.getClass().getComponentType();
		@SuppressWarnings("unchecked")
		T[] joinedArray = (T[]) java.lang.reflect.Array.newInstance(arrType1, mainArr.length + joinArr.length);
		System.arraycopy(mainArr, 0, joinedArray, 0, mainArr.length);
		try {
			System.arraycopy(joinArr, 0, joinedArray, mainArr.length, joinArr.length);
		} catch (ArrayStoreException e) {
			e.printStackTrace();
		}
		return joinedArray;
	}
	
	public final static ArrayList<String> toArrayList(String[] arr) {
		ArrayList<String> temp = new ArrayList<String>();
		return temp;
	}
	
	public final static String[] fromArrayList(ArrayList<String> arrList) {
		String[] temp = new String[arrList.size()];
		for (int i = 0; i < arrList.size(); i++) {
			temp[i] = arrList.get(i);
		}
		return temp;
	}
	
	private final static void sortDescending(int[] arr) {
		int[] temp = new int[arr.length];
		for(int i = 0; i < temp.length; i++) {
			temp[i] = arr[arr.length-i-1];
		}
		arr = temp;
		temp = null;
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

	private final static void swap(int[] arr, int left, int right) {
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

	private final static void mS(int l, int r, int[] arr, int[] temp) {
		if(l < r) {
			int m = l + (r - l) / 2;
			mS(l, m, arr, temp);
			mS(m + 1, r, arr, temp);
			m(l, m, r, arr, temp);
		}
	}

	private final static void m(int l, int m, int r, int[] arr, int[] temp) {
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