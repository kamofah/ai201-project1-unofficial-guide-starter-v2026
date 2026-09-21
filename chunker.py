"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import math
import re
from dataclasses import dataclass

import config
from ingest import Document

# A sentence ends at . ! or ? followed by whitespace. Not perfect — "Dr. Ruiz"
# and "8 a.m." will fool it — but it matches how these posts are actually
# written, and it keeps whole thoughts together far better than a character
# count does.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_sentences(text: str) -> list[str]:
    """Break one document into sentences, dropping anything that's only whitespace."""
    return [s.strip() for s in SENTENCE_END.split(text) if s.strip()]


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split each document into sentences, then into two halves.

    The documents here are short posts, and a fixed 800-character window cuts
    them mid-sentence for no reason. This splits on sentence boundaries
    instead, then puts the first half of the sentences in chunk 0 and the rest
    in chunk 1, so each chunk is made of whole sentences.

    With an odd number of sentences the first chunk gets the extra one: three
    sentences come out as 2 + 1.

    A document that is a single sentence stays a single chunk — there is
    nothing to put in the second half.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        sentences = split_sentences(doc.text)
        if not sentences:
            continue

        # Round up, so the first chunk is the bigger one when the count is odd.
        halfway = math.ceil(len(sentences) / 2)
        halves = [sentences[:halfway], sentences[halfway:]]

        index = 0
        for half in halves:
            if not half:
                continue
            chunks.append(
                Chunk(
                    text=" ".join(half),
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
            index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))