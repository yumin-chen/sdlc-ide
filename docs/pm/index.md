# Product Management Guide to the CEP Knowledge Hub

Welcome! This is your starting point for understanding our Complex Event Processing (CEP) system. Our goal is to give you a clear, non-technical overview of what CEP is, why it matters, and how you can use it to build smarter, more responsive products.

---

## 🚀 Quick Links

| Link                                   | Description                                                                                             |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **[CEP Fundamentals](./fundamentals.md)**  | Start here if you're new to CEP. Learn the core concepts in plain English.                              |
| **[Interactive Demos](./demos.md)**        | See CEP in action. Watch our interactive demos to understand how the system processes events in real-time. |
| **[Pattern Cookbook](../architecture/reference/pattern-cookbook.md)** | A library of common use-cases and the CEP patterns that solve them. Find inspiration for your next feature. |
| **[Scenarios](./scenarios.md)**            | Read detailed walkthroughs of how CEP is used to solve real-world problems like fraud detection and IoT.   |
| **[Trade-offs](./trade-offs.md)**          | Understand the key decisions and trade-offs we've made in our CEP architecture.                         |

---

## What is CEP? (The 1-Minute Explanation)

Imagine you're watching a security camera. You're not just looking at individual pictures; you're looking for a *sequence of events*—like someone walking to a door, trying a key, and then opening it.

That's what CEP does for our data. It finds meaningful patterns in the streams of events coming from our applications, in real-time.

**In short, CEP helps us answer questions like:**

*   "Did a user add an item to their cart, then apply a coupon, then abandon the purchase?"
*   "Are we seeing an unusual number of failed login attempts from the same IP address in the last 60 seconds?"
*   "Has a sensor in our factory sent a high-temperature warning three times in the last 5 minutes?"
