package teaType.data;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

import teaType.util.rigid.Print;

/**
 * The data-structure {@code TeaType} is my thread-safe
 * implementation of the data-structure ArrayList.<br><br>
 * 
 * It includes features of the stack and the queue like
 * 
 * @since JDK 1.91 ~ <i>2018</i>
 * @author Burak Günaydin <b>{@code (arsonite)}</b>
 * 
 * @param <T> Type-argument for the ArrayList.
 */

public class TeaType<T> implements List<T> {
	private boolean lock, dupli;
	private ArrayList<T> arr;

	public TeaType() {
		arr = new ArrayList<T>();
		reset();
	}
	
	public TeaType(int len) {
		arr = new ArrayList<T>(len);
		reset();
	}
	
	final void reset() {
		lock = false;
		dupli = true;
	}

	public final void allowDuplicates() { dupli = true; }

	public final void forbidDuplicates() { dupli = false; }

	public final boolean allowsDuplicates() { return dupli; }

	public final void lock() { lock = true; }

	public final void unlock() { lock = false; }

	public final boolean isLocked() { return lock; }

	/**
	 * 
	 * @param e
	 * @return
	 */
	public final boolean push(T e) {
		synchronized(this.getClass()) {
			if(!lock) {
				add(e);
				return true;
			}
			return false;
		}
	}

	public final T pop() throws Exception {
		synchronized(this.getClass()) {
			if(size() > 0) {
				return arr.remove(arr.size()-1);
			}
			throw new Exception("List is empty.");
		}
	}

	/**
	 * Placeholder
	 * 
	 * @param e
	 */
	public final boolean add(T e) {
		synchronized(this.getClass()) {
			if(!lock) {
				if(dupli) {
					arr.add(e);
					return true;
				}
				for(T t : arr) {
					if(e.equals(t)) {
						return false;
					}
				}
				arr.add(e);
				return true;
			}
			return false;
		}
	}

	/** @deprecated use {@link #add(T e)} instead */
	public final void add(int i, T e) {
		synchronized(this.getClass()) {
			arr.add(i, e);
		}
	}

	public final T get(int index) {
		synchronized(this.getClass()) {
			return arr.get(index);
		}
	}

	public final int size() {
		synchronized(this.getClass()) {
			return arr.size();	
		}
	}

	public final boolean isEmpty() {
		synchronized(this.getClass()) {
			for(T t : arr) {
				if(t!=null) {
					return false;
				}
			}
			return true;
		}
	}

	public final Iterator<T> iterator() {
		Iterator<T> it = new Iterator<T>() {
			private int i = 0;

			public final boolean hasNext() {
				synchronized(this.getClass()) {
					return i < arr.size() && arr.get(i) != null;
				}
			}

			public final T next() {
				synchronized(this.getClass()) {
					return arr.get(i++);
				}
			}

			public final void remove() {
				synchronized(this.getClass()) {
					throw new UnsupportedOperationException();
				}
			}
		};
		return it;
	}

	public final void print() {
		if(size() > 0) {
			String s = "Contents of list (size of " + size() + "):";
			System.out.println(s);
			Print.lines(s);
			for(int i = 0; i < arr.size(); i++) {
				System.out.printf("Class: %s | Content: \'%s\' | Index: %d%n",
						arr.get(i).getClass().getSimpleName(), arr.get(i).toString(), i);
			}
			System.out.println();
			return;
		}
		System.out.println("List is empty.");
	}

	public final void clear() {
		synchronized(this.getClass()) {
			arr.clear();
		}
	}

	public final void trim() {
		synchronized(this.getClass()) {
			ArrayList<T> temp = new ArrayList<T>();
			int c = 0;
			for(int i = 0; i < arr.size(); i++) {
				if(arr.get(i) != null) {
					temp.add(c, arr.get(i));
					c++;
				}
			}
			arr = temp;
		}
	}

	public final boolean contains(Object o) {
		return false;
	}

	public final Object[] toArray() {
		return null;
	}

	@SuppressWarnings("hiding")
	public final <T> T[] toArray(T[] a) {
		return null;
	}

	public final boolean remove(Object o) {
		return false;
	}

	public final boolean containsAll(Collection<?> c) {
		return false;
	}

	public final boolean addAll(Collection<? extends T> c) {
		return false;
	}

	public final boolean addAll(int index, Collection<? extends T> c) {
		return false;
	}

	public final boolean removeAll(Collection<?> c) {
		return false;
	}

	public final boolean retainAll(Collection<?> c) {
		return false;
	}

	public final T set(int index, T element) {
		return null;
	}

	public final T remove(int index) {
		synchronized(this.getClass()) {
			return arr.remove(index);
		}
	}

	public final int indexOf(Object o) {
		return 0;
	}

	public final int lastIndexOf(Object o) {
		return 0;
	}

	public final ListIterator<T> listIterator() {
		return null;
	}

	public final ListIterator<T> listIterator(int index) {
		return null;
	}

	public final List<T> subList(int fromIndex, int toIndex) {
		return null;
	}
}