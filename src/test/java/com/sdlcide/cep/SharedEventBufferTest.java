package com.sdlcide.cep;

import org.junit.jupiter.api.Test;
import java.nio.ByteBuffer;
import java.util.Map;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class SharedEventBufferTest {

    @Test
    void testRegisterAndRelease() {
        SharedEventBuffer buffer = new SharedEventBuffer();
        Event event1 = new Event(ByteBuffer.wrap("key1".getBytes()), "A", 1000, Map.of());
        UUID event1Id = event1.getEventId();

        // Register the event. Ref count should be 1.
        buffer.register(event1);
        assertNotNull(buffer.get(event1Id));

        // Add a reference.
        buffer.addReference(event1Id);

        // Release one reference. Event should still be in the buffer.
        buffer.release(event1Id);
        assertNotNull(buffer.get(event1Id));

        // Release the final reference. Event should be gone.
        buffer.release(event1Id);
        assertNull(buffer.get(event1Id));
    }

    @Test
    void testReleaseNonExistentEvent() {
        SharedEventBuffer buffer = new SharedEventBuffer();
        // Should not throw an exception
        buffer.release(UUID.randomUUID());
    }
}
