package com.sdlcide.cep;

public class Watermark {
    private long currentWatermark;

    public Watermark(long initialValue) {
        this.currentWatermark = initialValue;
    }

    public long getCurrentWatermark() {
        return currentWatermark;
    }

    public void advance(long newWatermark) {
        if (newWatermark > this.currentWatermark) {
            this.currentWatermark = newWatermark;
        }
    }
}
