package teaType.data;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

/**
 * The data-structure {@code SynchronizedArrayList} is my thread-safe implementation of the data-structure ArrayList.
 * Partially missing method-bodies are irrelevant for the required tasks.
 * 
 * <p>{@code 06.11.2017}
 * @author Burak Günaydin ({@code 853872})
 *
 * @param <T> Type-argument for the ArrayList.
 */

public class SynchronizedList<T> implements List<T> {
	private ArrayList<T> arr;

	public SynchronizedList() {
		arr = new ArrayList<T>();
	}

	public boolean add(T e) {
		synchronized(this.getClass()) {
			arr.add(e);
			return true;
		}
	}

	public void add(int i, T e) {
		synchronized(this.getClass()) {
			arr.add(i, e);
		}
	}

	public T get(int index) {
		synchronized(this.getClass()) {
			return arr.get(index);
		}
	}

	public int size() {
		synchronized(this.getClass()) {
			return arr.size();	
		}
	}

	public boolean isEmpty() {
		synchronized(this.getClass()) {
			for(T t : arr) {
				if(t!=null) {
					return false;
				}
			}
			return true;
		}
	}

	public Iterator<T> iterator() {
		Iterator<T> it = new Iterator<T>() {
			private int i = 0;

			public boolean hasNext() {
				synchronized(this.getClass()) {
					return i < arr.size() && arr.get(i) != null;
				}
			}

			public T next() {
				synchronized(this.getClass()) {
					return arr.get(i++);
				}
			}

			public void remove() {
				synchronized(this.getClass()) {
					throw new UnsupportedOperationException();
				}
			}
		};
		return it;
	}
	
	/*	PLEASE	IGNORE	*/
	
	/*
	 * (non-Javadoc)
	 * @see java.util.List#contains(java.lang.Object)
	 */
	
	public void clear() {
	}
	
	public boolean contains(Object o) {
		return false;
	}

	public Object[] toArray() {
		return null;
	}

	@SuppressWarnings("hiding")
	public <T> T[] toArray(T[] a) {
		return null;
	}

	public boolean remove(Object o) {
		return false;
	}

	public boolean containsAll(Collection<?> c) {
		return false;
	}

	public boolean addAll(Collection<? extends T> c) {
		return false;
	}

	public boolean addAll(int index, Collection<? extends T> c) {
		return false;
	}

	public boolean removeAll(Collection<?> c) {
		return false;
	}

	public boolean retainAll(Collection<?> c) {
		return false;
	}

	public T set(int index, T element) {
		return null;
	}

	public T remove(int index) {
		return null;
	}

	public int indexOf(Object o) {
		return 0;
	}

	public int lastIndexOf(Object o) {
		return 0;
	}

	public ListIterator<T> listIterator() {
		return null;
	}

	public ListIterator<T> listIterator(int index) {
		return null;
	}

	public List<T> subList(int fromIndex, int toIndex) {
		return null;
	}
}