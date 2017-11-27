package teaType.data;

import java.util.LinkedList;

import teaType.data.KeyValuePair;

public class Hashtable {
	protected LinkedList<KeyValuePair>[] array;
	protected int size;
	
	@SuppressWarnings("unchecked")
	public Hashtable(int size) {
		this.size = size;
		array = new LinkedList[size];
	}	

	private int hashFunction(Object key) {
		return key.hashCode() % array.length;
	}

	public Object put(Object key, Object val) {
		KeyValuePair kvp = new KeyValuePair(key, val);
		int index = hashFunction(key);
		int i = 0;
		if(isEmpty(index)) {
			array[index] = new LinkedList<>();
			array[index].add(kvp);
			return null;
		}

		for(@SuppressWarnings("unused") Object o : array) {
			if(key.equals(array[index].get(i).getKey())) {
				Object oldVal = array[index].get(i).getValue();
				array[index].get(i).changeValue(val);
				return oldVal;
			}
			i++;
		}
		
		array[index].add(kvp);
		return null;
	}

	public Object get(Object key) {
		int index = hashFunction(key);
		if(isEmpty(index)) {
			return null;
		}

		for(int i = 0; i < array[index].size(); i++) {
			if(key.equals(array[index].get(i).key)) {
				return array[index].get(i).value;
			}
		}
		return null;
	}

	public Object remove(Object key) {
		int index = hashFunction(key);
		try {
			for(int i = 0; i < array[index].size(); i++) {
				if(key.equals(array[index].get(i).key)) {
					Object temp = array[index].get(i).value;
					array[index].remove(i);
					return temp;
				}
			}
		} catch (java.lang.ArrayIndexOutOfBoundsException exc) {
			return null;
		}
		return null;
	}

	private boolean isEmpty(int index) {
		if(array[index] == null){
			return true;
		}
		return false;
	}

	public int getLength() {
		return size;
	}
}

class KeyValuePair {
	protected Object key;
	protected Object value;

	protected KeyValuePair(Object k, Object v) {
		key = k;
		value = v;
	}

	protected Object getKey() {
		return key;
	}

	protected Object getValue() {
		return value;
	}

	protected void changeValue(Object v) {
		value = v;
	}

	public String toString() {
		return value.toString();
	}
}