package teaType.data;

import java.util.LinkedList;

import teaType.data.KeyValuePair;

public class Hashtable {
	private LinkedList<KeyValuePair>[] list;
	private int size;
	
	@SuppressWarnings("unchecked")
	public Hashtable(int size) {
		this.size = size;
		list = new LinkedList[size];
	}	

	final int hashFunction(Object key) {
		return key.hashCode() % list.length;
	}

	public Object put(Object key, Object val) {
		KeyValuePair kvp = new KeyValuePair(key, val);
		int index = hashFunction(key);
		int i = 0;
		if(isEmpty(index)) {
			list[index] = new LinkedList<>();
			list[index].add(kvp);
			return null;
		}

		for(@SuppressWarnings("unused") Object o : list) {
			if(key.equals(list[index].get(i).getKey())) {
				Object oldVal = list[index].get(i).getValue();
				list[index].get(i).changeValue(val);
				return oldVal;
			}
			i++;
		}
		
		list[index].add(kvp);
		return null;
	}

	public Object get(Object key) {
		int index = hashFunction(key);
		if(isEmpty(index)) {
			return null;
		}

		for(int i = 0; i < list[index].size(); i++) {
			if(key.equals(list[index].get(i).key)) {
				return list[index].get(i).value;
			}
		}
		return null;
	}

	public Object remove(Object key) {
		int index = hashFunction(key);
		try {
			for(int i = 0; i < list[index].size(); i++) {
				if(key.equals(list[index].get(i).key)) {
					Object temp = list[index].get(i).value;
					list[index].remove(i);
					return temp;
				}
			}
		} catch(ArrayIndexOutOfBoundsException exc) {
			return null;
		}
		return null;
	}

	final boolean isEmpty(int index) {
		if(list[index] == null){
			return true;
		}
		return false;
	}

	public int getLength() {
		return size;
	}
}

class KeyValuePair {
	protected Object key, value;

	public KeyValuePair(Object k, Object v) {
		key = k;
		value = v;
	}

	final Object getKey() { return key; }

	final Object getValue() { return value; }

	final void changeValue(Object v) { value = v; }

	public String toString() { return value.toString(); }
}