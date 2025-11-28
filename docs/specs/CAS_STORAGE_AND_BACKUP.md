# 📄 **Jules CAS Storage & Backup Architecture (Draft Document)**

## **1. Purpose**

This document defines how Jules handles **generated artifacts**, **content-addressed storage (CAS)**, and **backup strategies** in a **local-first, deterministic, multi-agent cognitive OS**.

The goal is to ensure:

* Git remains fast and small
* All generated content is preserved
* Data loss is impossible
* Architecture scales to millions of artifacts
* Local-first operation with optional cloud sync
* Deterministic provenance for every artifact

---

## **2. Overall Principle**

### **Source-of-truth → Git**

### **Generated or large content → CAS**

Git stores:

* human-authored code
* schemas
* metadata
* policies
* references to CAS objects

CAS stores:

* all agent outputs
* LLM-generated content
* artifacts
* embeddings
* logs
* binary data
* large documents
* knowledge nodes

---

## **3. CAS Layout**

CAS uses **content-addressed immutable objects**:

```
~/.jules/cas/
  ab/cdef123456...
  fe/9988aa...
  ...
```

Hash is `sha256`, guaranteeing:

* immutability
* deduplication
* reproducibility
* easy syncing
* simple backup

---

## **4. Git Metadata Model**

Git DOES NOT store generated artifacts.

Git stores small metadata commits referencing CAS:

```
{
  "task_id": "123",
  "agent": "jules",
  "inputs": ["sha256:a1b2c3..."],
  "outputs": ["sha256:d4e5f6..."],
  "summary": "Model generated summary",
  "timestamp": 1700000000
}
```

This keeps Git:

* fast
* clean
* deterministic
* human-auditable

---

## **5. Why Not Store Artifacts in Git**

Generated artifacts in Git cause:

* massive repo bloat
* slow clones
* slow merges
* packfile explosion
* corrupted history via LLMs
* unbounded growth

Git is optimized for *source*, not *data*.

CAS solves these issues.

---

## **6. CAS Backup Architecture**

### ✔ **Primary CAS** — Local Filesystem

All agents read+write directly:

```
~/.jules/cas
```

Fastest and fully offline.

---

### ✔ **Secondary Backup — Syncthing (Local-First Sync)**

Provides encrypted sync between personal devices:

```
Laptop  ←→  Desktop  ←→  Home Server
```

Syncthing advantages:

* peer-to-peer
* encrypted
* versioned
* zero cloud requirement
* excellent for a personal knowledge OS

---

### ✔ **Cold Backup — Private Git Blob Repository**

A separate Git repository (NOT the project repo) is used to store the CAS directory as raw files.

```
~/.jules/cas-backup-git/
  .git/
  ab/cdef...
  fe/1234...
```

Workflow:

```
rsync ~/.jules/cas/ ~/.jules/cas-backup-git/
git add .
git commit -m "CAS backup <timestamp>"
git push origin main
```

Properties:

* Git used only as a blob vault
* Incremental backups
* Full history retention
* Private, encrypted
* Separate from source repo

This is extremely reliable because CAS objects:

* are immutable
* do not change once created
* compress well
* append-only

Ideal for long-term archival.

---

### ✔ **Optional Tier — Private S3/MinIO Backend**

If you need multi-agent or multi-device at scale:

Use MinIO locally → sync to S3/R2/B2.

Benefits:

* high durability
* managed replication
* cheap cold storage
* versioning
* global access

---

## **7. Why This 3-Tier Strategy Is Optimal**

You get:

### 🔹 **Local-first performance**

Agents always run against local CAS.

### 🔹 **Guaranteed data durability**

Syncthing + Git vault ensure no loss.

### 🔹 **Offline operation**

Your cognitive OS works anywhere.

### 🔹 **Infinite scalability**

Millions of immutable CAS objects without slowing Git.

### 🔹 **Deterministic provenance**

Git metadata + CAS provides perfect reproducibility.

### 🔹 **Agent safety**

LLMs cannot accidentally mutate or delete CAS objects.

### 🔹 **Human safety**

Git remains clean and readable without artifact spam.

---

## **8. File/Directory Structure Summary**

```
project/
  git/                      → normal project repo
    .git/
    src/
    schemas/
    jules-meta/             → metadata, not artifacts

~/.jules/
  cas/                      → primary CAS store
    aa/bb...
    ...
  cas-backup-git/           → private Git blob backup repo
    .git/
  syncthing/                → optional folder for sync
  config/                   → agent configuration
```

---

## **9. Restoration Procedure**

To restore CAS on a new machine:

1. Clone the **CAS backup Git repo**
2. Restore to `~/.jules/cas`
3. Clone project Git repo
4. Jules automatically resolves CAS pointers

Everything is reproducible.

---

## **10. Future Extensions**

This architecture supports:

* deduped “knowledge nodes”
* CRDT-like partial sync
* distributed agent memory
* versioned embeddings
* deterministic DAG reconstruction
* provenance queries
* offline agent replay

It is the ideal foundation for a **local-first AI operating system**.
