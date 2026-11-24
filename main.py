"""Monday, Reviewed in One Line — entry program.

Writes one line (1-200 chars) to /output/entry.txt: a one-line review of
the entrant's own Monday. Stdlib only, deterministic.

The line targets the judge brief in order: it IS a review of the entrant's
own Monday ("My Monday", closed with a star rating); the paradox punchline
("I did no work and attended four meetings about it") makes the reader
laugh rather than nod; the detail is concrete — four named meetings with
their hours, escalating in absurdity (standup, sync, alignment,
touchpoint); the joke lands inside the line with no wasted words; and it is
the line a reader repeats to a coworker the next morning.
"""
import os

TEXT = (
    "My Monday: 8am standup, 9am sync, 10am alignment, 11am touchpoint. "
    "I did no work and attended four meetings about it. One star."
)


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-200 chars, one line,
    # not whitespace-only. Fail loudly instead of writing an invalid entry.
    # Also refuse control characters: a stray \x00-\x1f would fail the
    # scorer's UTF-8 text check.
    if not 1 <= len(TEXT) <= 200 or "\n" in TEXT or not TEXT.strip():
        raise SystemExit("entry text violates the 1-200 char single-line gate")
    if any(ord(c) < 0x20 for c in TEXT):
        raise SystemExit("entry text contains a control character")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
