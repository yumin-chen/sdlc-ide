# The CEP Pattern Cookbook

This document is a library of common, reusable patterns for solving business problems with Complex Event Processing. Use this cookbook to find inspiration for new features and to translate your product requirements into a technical design.

---

## 1. Simple Sequence

**Use Case:** Detect when a user performs a specific sequence of actions in order.

*   **Example:** A user adds an item to their cart, then proceeds to checkout, then completes the purchase.
*   **Natural Language:** "Find every time a user does A, then B, then C."
*   **Pseudo-code:**
    ```
    PATTERN (A, B, C)
    WHERE A.eventType = "item_added_to_cart"
      AND B.eventType = "checkout_started"
      AND C.eventType = "purchase_completed"
    CORRELATE BY user.id
    ```

---

## 2. Sequence with a Time Window

**Use Case:** Detect a sequence of events that must occur within a specific time frame.

*   **Example:** A user logs in and then successfully resets their password within 10 minutes.
*   **Natural Language:** "Find every time a user does A, then B, all within X minutes."
*   **Pseudo-code:**
    ```
    PATTERN (A, B)
    WITHIN 10 minutes
    WHERE A.eventType = "user_login"
      AND B.eventType = "password_reset_success"
    CORRELATE BY user.id
    ```

---

## 3. Sequence with a Choice (OR)

**Use Case:** Detect a sequence where one of the steps can be one of several possible events.

*   **Example:** A user adds an item to their cart, then either applies a coupon OR views a recommended item.
*   **Natural Language:** "Find every time a user does A, then either B or C."
*   **Pseudo-code:**
    ```
    PATTERN (A, (B OR C))
    WHERE A.eventType = "item_added_to_cart"
      AND B.eventType = "coupon_applied"
      AND C.eventType = "recommendation_viewed"
    CORRELATE BY user.id
    ```

---

## 4. Absence / Negative Lookahead

**Use Case:** Detect when an event does *not* happen after another event.

*   **Example:** A user adds an item to their cart but does *not* complete the purchase within 1 hour (cart abandonment).
*   **Natural Language:** "Find every time a user does A, but is not followed by B within X minutes."
*   **Pseudo-code:**
    ```
    PATTERN (A, NOT B)
    WITHIN 1 hour
    WHERE A.eventType = "item_added_to_cart"
      AND B.eventType = "purchase_completed"
    CORRELATE BY user.id
    ```

---

## 5. Windowed Aggregation

**Use Case:** Count or aggregate events over a specific time window.

*   **Example:** Count the number of failed login attempts from a single IP address in the last 60 seconds.
*   **Natural Language:** "Count the number of times event A happens within X seconds."
*   **Pseudo-code:**
    ```
    AGGREGATE COUNT(A)
    OVER 60 seconds
    WHERE A.eventType = "login_failed"
    GROUP BY ip_address
    HAVING COUNT(A) > 5
    ```

---

## Templates

### Fraud Detection Template

*   **Scenario:** A user makes a purchase with a new credit card, from a new device, for an unusually large amount.
*   **Pattern:**
    ```
    PATTERN (A, B, C)
    WITHIN 5 minutes
    WHERE A.eventType = "new_card_added"
      AND B.eventType = "new_device_login"
      AND C.eventType = "purchase_completed" AND C.amount > 1000
    CORRELATE BY user.id
    ```

### IoT Monitoring Template

*   **Scenario:** A sensor reports a high temperature reading three times in a row within a 1-minute window.
*   **Pattern:**
    ```
    PATTERN (A, A, A)
    WITHIN 1 minute
    WHERE A.eventType = "temperature_reading"
      AND A.value > 90
    CORRELATE BY sensor.id
    ```
