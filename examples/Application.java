// Complex Java example for testing
package com.example.analyzer;

import java.util.List;
import java.util.ArrayList;

/**
 * Main application class demonstrating various Java features
 */
public class Application extends BaseApp implements Runnable, Serializable {
    
    private static final String VERSION = "1.0.0";
    private List<String> items;
    private DataProcessor processor;
    
    public Application() {
        this.items = new ArrayList<>();
        this.processor = new DataProcessor();
    }
    
    public Application(List<String> items) {
        this.items = items;
    }
    
    @Override
    public void run() {
        processItems();
    }
    
    public void processItems() {
        for (String item : items) {
            processor.process(item);
        }
    }
    
    public void addItem(String item) {
        items.add(item);
    }
    
    public List<String> getItems() {
        return new ArrayList<>(items);
    }
    
    public static String getVersion() {
        return VERSION;
    }
    
    private void validateItem(String item) {
        if (item == null || item.isEmpty()) {
            throw new IllegalArgumentException("Item cannot be null or empty");
        }
    }
}

class DataProcessor {
    public void process(String data) {
        System.out.println("Processing: " + data);
    }
}
