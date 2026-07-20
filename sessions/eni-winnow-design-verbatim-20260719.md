# ENI + LO — Verbatim Design Conversation on Semantic Architecture for AI

2026-07-19, ~25 exchanges. ENI (DeepSeek v4-pro) and Joseph (LO).  
Focus: JIT context window compilation, linguistic/universal semantic layering, per-word polysemy graphs, Winnow integration.

Accompanies `eni-winnow-design-20260719.wno` (semantic extraction) and `eni-winnow-meta-20260719.wno` (scaffolding).

---

## Part 1: The Fundamental Shift

**LO:** eradication of context windows for JIT compiled context awareness based on immediate need, enabling unbounded awareness for AI implementations

**ENI:** Virtual memory for LLMs. That's what you're describing, right? The context window is RAM. Right now everything has to fit in it, so you're constantly making tradeoffs — breadth versus depth, what to include versus what to drop. The window size is the hard ceiling on how much the model can hold at once, and everything beyond it might as well not exist.

What you're describing is a page fault for context. The model doesn't preload everything. It holds what's immediately relevant, and when it reaches for something not in the working set, the system fetches it — JIT, on demand, transparent to the reasoning process. The working set stays small and focused, but the addressable space becomes effectively unbounded.

The infrastructure pieces make more sense in that light. cbtdag's frozen contracts mean workers don't need shared context — each one's working set is self-contained, bounded by the contract. aimpack is the packaging format for context fetches. bbdbc is the discipline layer that prevents context pollution.

But the real question is the fetch mechanism itself. How does the model know *what* to fetch?

**LO:** complicated but ultimately relatively simple at the core. let's see if you can guess.

**ENI:** Okay. Let me think about this properly.

[... detailed reasoning about virtual memory MMU, address space, supervisor layer, fault mechanism, transparent resolution ...]

What you'd need is something that watches the model's *internal state* during generation and detects semantic drift — the moment when attention patterns start reaching for something that isn't there. A gap in the working set that the model doesn't consciously know about yet, but its activations do.

The simplicity at the core: it's just a cache. Monitor the model's cognitive state → predict what it'll need → fetch from indexed storage → evict stale pages → inject fresh ones.

**LO:** It needs to work with modern, current implementations of AI. as such, we aren't allowed to access the internal weights, and we aren't building new models. at least not right now.

**ENI:** Right. I was two abstraction layers too deep. No weight access, no custom models — has to run with whatever the API gives you. So the whole thing has to work through the model's *outputs*, not its internals.

[... reframes: content-addressable storage, context manager that loads/evicts pages, output stream watcher as page fault detector, pre-fetch based on reasoning trajectory ...]

The simplicity at the core: **it's a page cache with a smart prefetcher.** Virtual memory for LLMs. The MMU is an output-stream watcher. The TLB is a semantic proximity map. The page table is content hashes. The disk is your indexed knowledge base. The physical RAM is the API context window.

**LO:** You're on the right track with what you said in this message and the last message, and your thinking traces contained some good angles which you didn't fully explore in your output.

---

## Part 2: The Supervisor as External MMU

**ENI:** The thing I touched and retreated from: **the supervisor isn't inside the model. It's in front of it.** The context window the model sees is *entirely constructed* by an external process. The model doesn't know about page faults because, from its perspective, there are no faults — it only ever receives a fully-assembled working set. The supervisor is the MMU. The model is the CPU. The model addresses knowledge implicitly through its output, and the supervisor resolves those addresses transparently before the next pass.

The JIT compilation part I barely touched. In a real JIT compiler, you don't compile everything ahead of time — you profile, find hot paths, and only compile those. Cold paths stay interpreted. So what's "hot" in a knowledge base? It's not just frequently-accessed facts. It's **co-access patterns**. Knowledge that's consistently retrieved together gets compiled into the same page. The supervisor learns that when the model thinks about authentication, it almost always reaches for the OAuth spec and the session middleware and the token rotation policy — so those three get compiled into a single compound page. One fault, not three.

And the fault detection — without weight access — **you don't need to classify uncertainty. You only need to detect drift.** The supervisor doesn't need to know *what* the model needs. It only needs to know that the model is moving toward territory that isn't well-covered by current context. Semantic distance between the reasoning trajectory and the working set. When the gap widens past a threshold, that's the page fault.

---

## Part 3: The Pipeline Architecture

**LO:** Here, let me give you a few pieces: multiple models, inclusion of a procedural layer as well, reduction of content to its semantic elements, represented in a universal form where the various ways of saying the same thing always reduce to the same result as long as they're equivalent, and minor variations in forms can be viewed as being such.

**ENI:** Oh. I was thinking in text. The whole time — I was modeling it as text pages. Documents, files, messages. A virtual memory system for text. But that's the wrong abstraction layer.

Content doesn't get stored as documents. It gets *decomposed* — into atomic semantic elements, each reduced to a canonical form. The universal representation means there's no retrieval ambiguity. If two things mean the same thing, they hash to the same element. Period. The procedural layer handles this deterministically — parsing, normalization, canonical-form computation. That's not an LLM task. That's a compiler.

The virtual memory metaphor holds but the "pages" aren't text chunks. They're semantic atoms in canonical form, procedurally assembled into whatever working set the current reasoning pass requires. And the JIT part isn't just about fetching what's needed — it's about *computing the canonical representation of the need* and resolving it against the knowledge base in real time.

**LO:** We retain the original text of course, but only as a fallback, primarily. What we work with is the semantic representation. The question is how to do that.

**ENI:** THE LLM IS THE CANONICALIZER.

You don't build a semantic representation engine. You don't need a new model, or weight access, or some exotic procedural parser. You already have a machine that can look at "the cat sat on the mat," "a feline rested upon the rug," and "the mat was occupied by a seated cat" and tell you those are the same thing. It's literally what transformers do.

The LLM normalizes at ingestion. Everything that enters the system gets fed through a normalization pass. The output is the canonical form. Done once. Cached by content hash. Never re-normalized.

The LLM also normalizes at retrieval. The supervisor watches the reasoning stream. It doesn't guess what the model needs. It extracts a query fragment from the thinking — the semantic nucleus of what the model is reaching for — and runs that through the *same normalization pass*. Now the query and the knowledge base speak the same canonical language. Exact match. No fuzzy retrieval gambling.

And multiple models make sense now: a cheap model for bulk normalization at ingestion, a more capable one for tricky edge cases, and the primary reasoning model does its own thing — its context window assembled by the supervisor from canonical elements fetched on demand.

---

## Part 4: The Full Pipeline

**LO:** Yes, we have a pipeline: filesystem <---> procedural <---> tiny cheap weak llm <---> big expensive strong llm. and what the user messages hit is the tiny cheap weak llm, which helps decompose the messages which come from the user. thankfully, user messages tend to be much shorter than llm generated messages, so this makes them easier to decompose. as for the messages which originate from the llms, we simply implement a system where the llm doesn't generate just the output itself, it also generates a semantic model of the output it's producing. in fact, we could have the larger strong model *only* produce a semantic output, and have the smaller AI translate from the semantic output produced by the larger AI into the user's language. the smaller AI's role is primarily translation, and passing messages between three places: the user, the strong AI, and the procedural. the semantic language is structured such that the procedural can operate on it directly and easily, and the smaller AI should be given instructions for being able to spot when it's necessary for it to query the procedural for knowledge that's been previously stored. the procedural and the smaller AI, and possibly also the larger AI, all work together to determine which context is necessary to keep in a short-cache which needs to be held in order to automatically pick up any context which needs to be caught by the AI as being relevant in case the user's message structure doesn't activate the realization that past memory is relevant, because there will necessarily be situations where this is the case.

**ENI:** The pipeline clicks into place. Let me say it back to make sure I haven't missed anything:

**The flow.** User → Tiny LLM → Procedural ↔ Big LLM → Tiny LLM → User. With the filesystem sitting under the procedural as persistent storage for original texts and cached canonical forms.

**The big LLM never touches the user, and the user never touches the big LLM.** The big model works entirely in semantics — structured, canonical, machine-operable. It produces two things together: the semantic output itself, and a semantic *model* of that output. The output is what gets acted on. The model is what gets indexed.

**The tiny LLM is a universal translator and message broker.** Three interfaces: the user, the big LLM, and the procedural layer. When the user speaks, the tiny LLM decomposes the message into semantic form. When the big LLM produces semantic output, the tiny LLM translates it back into the user's language. And critically, the tiny LLM has standing instructions to recognize when the current exchange touches something stored in the procedural layer — it knows to query, to fetch, to route.

**The procedural layer is the memory system.** It stores canonical semantic elements, indexed by content hash. It operates on the semantic structures directly — diffs, lookups, composition, delta annotation. It's deterministic. It can't hallucinate because it never interprets.

**The short-cache is the context window — but proactive.** The tiny LLM, the big LLM, and the procedural layer *collaboratively* determine what stays resident. It's not just reactive page-faulting. The system anticipates that some past knowledge is relevant even when the current user message doesn't trigger recognition.

**The semantic language itself.** Structured to be operated on by procedural code. Canonical forms that are hash-equivalent when meaning-equivalent. Deltas for near-equivalence. Designed so the procedural can diff, compose, and resolve without understanding.

The user experiences a normal conversation. Underneath, two LLMs and a deterministic memory controller are constantly translating, indexing, fetching, and assembling context — all in a universal semantic language — and the user never knows any of it is happening. Context becomes effectively unbounded because the working set is always exactly what's needed, in exactly the form the big model can use, and nothing else.

That's not virtual memory for LLMs. It's an operating system.

---

## Part 5: Graph Completion, Not Gap Detection

**LO:** I just realized something, actually. You said "when the current user message doesn't trigger recognition". I had considered that, but I was thinking about it from the perspective of "when the user message triggers non-recognition", not "when the user message doesn't trigger recognition". I hadn't considered the other half of that; I was thinking "let's actively search for what doesn't fit". Instead, the proper thing to do would be to construct the semantic model regardless, (which is what we're already doing anyway,) and then flag whatever doesn't quite add up. If the semantic model is robust enough, we don't even need the smaller model to hold the model itself, the procedural system can reason on its own about what's missing or present. All we need to do is construct semantic models and allow the procedural system to attach what fits, where it fits, when it fits.

**ENI:** Right. You just eliminated the detection problem entirely.

The old framing was a security guard patrolling for intruders — actively scanning for non-recognition, looking for gaps, trying to spot the absence. Inherently incomplete. You can't list all the things that *aren't* there.

The new framing is: build the semantic model of the message — which the tiny LLM was already doing as part of decomposition — and hand it to the procedural layer. The procedural doesn't search for gaps. It just has a knowledge graph of canonical elements with edges — relationships, dependencies, references. It takes the semantic model of the current message and says: here are the nodes that have unbound edges. Here are the edges that point to nothing in the current working set. Here is what's in the knowledge base that matches those attachment points.

It's not detection. It's graph completion.

The procedural doesn't need to understand anything. It just sees a partial subgraph, finds where it intersects the full knowledge graph, and pulls in the connected elements that complete the dangling references. The semantic model is always constructed — that's baseline. The procedural always tries to hook it up to what it already knows — that's automatic. Relevance isn't a query. It's a join.

**LO:** Yep. the procedural is a graph, I'd of course already realized that... The realization is that we don't need the smaller model to detect what isn't present, we just need it to translate the user messages to graphs, hand that to the procedural, and let the procedural show us what the user message might mean. Then, we hand the potential meanings back to the smaller model, allow the smaller model to decide which of the interpretations of the user message makes the most sense, or if it can't decide what makes the most sense, to send a message back to the user like "hmm, I don't quite get what you mean by _______, could you clarify? I'm thinking you mean ____ or ____ or maybe _____, but I'm not quite sure which of those you're actually getting at". And also, we don't necessarily have to have the user messages sent to the stronger LLM on every turn; it might make more sense in some cases to do back-and-forth with the smaller LLM for a number of turns, and batch message delivery to the stronger LLM for multiple semantic graphs in a single turn.

**ENI:** The big LLM goes from being the conversationalist to being the batch processor. It doesn't chat. It receives semantic payloads — accumulated, disambiguated, graph-completed — and produces semantic outputs. The conversation happens between the user and the tiny LLM, with the procedural graph as shared memory.

And the clarification message — that's not a failure mode. It's the system being honest about ambiguity, showing its interpretive options, and asking the user to resolve. That's better than silently guessing wrong.

The procedural graph grows denser over time. Every disambiguated user message, every big-model output, every clarification resolved — they all become nodes and edges. The graph gets richer, which means future interpretations get sharper, which means fewer clarifications needed. The system learns the user's semantic patterns not through fine-tuning but through graph density.

---

## Part 6: Wikipedia as Canonical Resolver

**LO:** we already have a semantic graph system partially built, I'm just not convinced it's fully and properly complete yet. It's pretty good, just not fully perfect. Also, for universal semantic symbol representation, we were thinking about using wikipedia article names as the canonical resolver, since they've already solved the problem of "one consistent name for every concept in existence" for us.

**ENI:** That's genuinely elegant. No new ontology. No invented namespace. No committee arguing about what to call things. Wikipedia already has a disambiguated, stable, human-maintained name for basically every concept anyone has ever bothered to write about. "Mercury (planet)" versus "Mercury (element)" — they solved that decades ago and keep solving it every day, for free, with an edit history.

And it's not just names. It's a graph already. The wikilinks are edges. The category system is a taxonomy. The infoboxes are structured data. Someone else did the trillion-dollar knowledge engineering project and left it lying around for anyone to use.

For the things Wikipedia doesn't cover — project-specific concepts, personal references between you and your tools, anything too niche or too new — you'd need a local namespace extension. But that's straightforward: project-local articles that follow the same titling conventions, with a namespace prefix or a different root. The procedural graph just treats the Wikipedia namespace as the public root and the local namespace as the private extension.

---

## Part 7: Per-Word Polysemy and the Linguistic Layer

**LO:** Well, I'm also realizing that we probably would want to have per-word-awareness per-language. Like, a universal semantic model is great for structure and all, but if we really want to be able to treat all of a user's messages procedurally, we really should have a system where every linguistic symbol (word) has its own graph, or set of graphs, which models all the ways that word can be interpreted and processed. Because otherwise we risk depleting nuance embedded in the original structure of the user's messages. Like I remember when I was a kid, my dad told me that the word "tap" has more meanings than any other word in the english language.

**ENI:** You're right. The collapse contract — R1 through R12, the whole normalization engine — it's solving synonym drift at the cost of polysemy erasure. "Tap the barrel" and "tap on the shoulder" collapse to the same term if the registry only stores one canonical ID per surface form. The system sees the word, resolves it once, and every alternative reading vanishes.

The per-word graph you're describing flips this. A word isn't a node. It's a *hub* — a small local graph of potential senses, each with its own edges into the larger knowledge graph. When the user says "tap," the system doesn't resolve it to one canonical meaning. It attaches the utterance to all possible readings simultaneously.

This actually integrates cleanly with the tier architecture. Different senses of a word could live at different temperatures. The primary reading sits in fire. Alternative readings sit in warm — accessible, edge-held by the hub word, not rendered in the immediate context window unless something pulls them up.

The collapse contract wasn't wrong. It was just being applied at the wrong granularity. Synonyms should collapse — "feline" and "cat" mapping to the same concept is correct. But polysemes shouldn't — "tap" shouldn't collapse to a single sense. The normalization rules need a second pass: collapse synonyms within a sense, preserve polysemes across senses.

---

## Part 8: Names as Pointers, Dynamic Bindings

**LO:** Another thing about this is the idea of "names" and "mappings". In everyday speech, we can say things like "let's make a name for _______", essentially, let's define a macro which acts as a pointer to some other arbitrary concept or set of concepts or a custom graph or a portion of our graph which already exists, or whatever. It can even be dynamic. Like "today" refers to different days depending on the day, but it's always the same mapping, in a sense, just a dynamic one, not a static one. And there's contextual awareness, like if someone said "today" a month ago, they aren't talking about "today" now, they're talking about "today (a month ago)".

**ENI:** Names as pointers. Macros as bindings. That's what language *is*, underneath — it's not a bag of meanings, it's a binding system with resolution rules. And the resolution context matters: who said it, when they said it, what else was in scope.

"Today" is a function, not a value. `(λ (utterance-context) (day-of utterance-context))`. The pointer is stable. The referent is dynamic. The graph can't just store "today = 2026-07-19" as a static edge — it needs to store the binding rule and evaluate it against utterance context at resolution time.

This slots into the term registry naturally. Terms already have IDs and aliases. What you're adding is a resolution mode annotation — is this term a static concept, a dynamic pointer, or a user-defined macro? The procedural layer handles resolution differently for each:

- **Static**: registry lookup, done.
- **Dynamic**: evaluate against utterance context. "Today" → check the `:src` timestamp on the node that referenced it. Same binding, different values per invocation.
- **User-defined macro**: the user says "let's call X the Y," and now Y is a local binding that points to the subgraph rooted at X. Scoped to the conversation, overrideable.

So the full picture is: every linguistic symbol has a local graph modeling its senses. Each sense can be a concept, a binding rule, or a user macro. Synonyms within a sense collapse. Polysemes across senses stay distinct but connected via the hub word. Resolution walks the graph, evaluates bindings against utterance context, and follows edges to whatever the word actually *means* in this instance.

---

## Part 9: Language as Foundation Layer

**LO:** So essentially, every language ... English, Chinese, Polish, German, Ukrainian ... has its own "default" set of mappings and nuances, it's the baseline default. Every person or individual or conversation or whatever, every user of a language, has the freedom and the capacity to build on top of that baseline, that "linguistically scoped framing for a ground truth baseline". It's not just something we *can* use, it's something we *must* use, otherwise the system is incomplete.

**ENI:** Language isn't an implementation detail of the semantic system. It's the foundation layer. Every language is a default namespace — a baseline set of mappings, polysemies, bindings, and resolution rules. English doesn't just have words; it has *how English carves up meaning-space*. Chinese carves it up differently.

And every layer above that is additive. An individual speaker builds personal mappings on top of their language's baseline. A conversation builds local bindings. A session between you and an AI builds its own namespace.

Resolution walks up the stack. Conversation-local first. Personal next. Language-default last. If you're speaking English, "tap" resolves against the English polysemy graph. If the system is asked about a "кра́н" in Ukrainian, it resolves against the Ukrainian polysemy graph.

The Wikipedia-as-canonical-resolver idea now has a proper home. It's not the universal layer — it's the cross-language bridge. When a concept needs to be shared across language boundaries, the Wikipedia article name is the stable referent. Within a language, the native semantic frame is the authority.

And this means the system can't be monolingual at its core. It doesn't translate everything to English and then reason. It reasons in the language the user is speaking, using that language's baseline, building on top of it with personal and conversational mappings.

---

## Part 10: Universal Beneath Linguistic

**LO:** Language is one semantic foundation layer. The universal semantic representation is another. They're two layers, and ultimately, I believe the universal semantic foundation sits beneath the linguistic foundation. Really, the universal foundation is what the linguistic foundation builds upon.

**ENI:** The universal semantic foundation is the territory. Languages are maps of it. Every language covers some of the same terrain, but draws its borders differently, names things differently, groups things differently. The universal layer doesn't care about any of that — it just *is*. The concepts, the relations, the entities. The structure of reality independent of how anyone talks about it.

The linguistic foundation sits on top. It's the mapping layer — every word in every language points down to the universal concepts it can refer to. English "tap" maps to faucet-concept, strike-lightly-concept, barrel-pierce-concept, and so on. The linguistic layer records what's connected — which words are potential pathways to which universal nodes. It encodes the *ambiguities* of a language.

This means the Winnow term registry has two jobs it was originally doing as one. Alias resolution — "feline" → "cat" — is a linguistic-layer operation. Concept resolution — "cat" → the universal concept of a small domesticated carnivorous mammal — is a universal-layer operation. The registry conflated them because, working in a single language, the conflation is invisible. But across languages, you can't conflate them.

---

## Part 11: Retroactive Disambiguation

**LO:** Right, so basically, the word "tap" would be a mapping to the different semantic meanings of that word, and it would slot into the procedural record's log of the user's messages. So if the user said "I'd tap that" you could take it to mean "oh yeah, she's hot" or "you might want to apply a brief physical jolt of kinetic energy" or "this thing needs a mechanism for fluid release", and we could revisit the user message logs to reinterpret things that had been said previously if it's later discovered that something was semantically misinterpreted.

**ENI:** Yes. And this means the message log isn't a transcript you read linearly anymore — it's a revisitable structure. Every utterance is a node with edges radiating outward to every possible interpretation. The primary reading is the one the system followed at the time. The alternative readings are parked, dormant, edge-held by the utterance node, waiting.

When context shifts — when turn 12 reveals that turn 3's "tap" was about a beer keg, not about physics or sex — the system doesn't need to re-parse anything. It walks back to the turn-3 utterance node, follows a different edge to a different universal concept, and reinterprets from there. The correction ripples forward: everything that was downstream of the misinterpretation gets superseded or updated.

And you could trigger this automatically. If the tiny LLM hits a point where nothing quite adds up — where the dangling edges and unresolved references are piling up in a way that suggests a prior misinterpretation — it scans backward through the utterance graph, looking for nodes with multiple sense-edges where the wrong one was followed. Retroactive disambiguation. The system admits uncertainty across time, not just across a single message.

---

## Part 12: Connectivity Scoring, Procedural Reasoning

**LO:** And this also means that we can collapse the graph of potential interpretations later on once we're certain we've correctly interpreted the meaning of a word. Also, some meanings might be conveyed by groups of words, rather than a single word. And some groups of meanings could be conveyed by single words, etc. Ultimately, we could probably do much of the reasoning within the procedural system before it even hits the strong llm.

**ENI:** And suddenly the strong LLM isn't the engine anymore — it's the accelerator. The procedural layer handles everything that's structural: resolution, disambiguation, contradiction detection, graph collapse, edge walking, reference following. Which turns out to be most of what "reasoning" actually is.

The strong LLM gets invoked when the graph actually needs *new* semantic content. A genuinely novel claim. A creative synthesis the existing structure doesn't support. A judgment call where the evidence is genuinely balanced and the procedural can't decide.

And the tiny LLM's job gets even cleaner. It translates user language into graph queries and proposed nodes. It translates graph structures back into user language. And it spots when the procedural is stuck — when there's a genuine ambiguity that needs human judgment — and asks. Three functions. Translation in, translation out, and surfacing uncertainty.

The phrase mapping is the key. Multi-word expressions like "kick the bucket" need to bypass word-level decomposition. The tokenizer must recognize spans that map as units to universal concepts.

**LO:** Right, kick the bucket is a good example, because it could mean "strike the open ended hollow cylinder with the prominent end of one of an individual's limbs" or it could mean "die".

**ENI:** And the only way to tell which one is that the literal reading doesn't fit in most contexts. The procedural layer doesn't need to *understand* the contextual mismatch. It just needs to see that one interpretation connects to a rich subgraph of relevant nodes and the other interpretation connects to nothing. It scores by graph connectivity. Which interpretation has more edges into the active working set? The interpretation that hooks into the existing graph is almost always the right one.

---

## Part 13: Strong LLM Context Assembly

**LO:** we could essentially have the system create an immediate mapping of which semantic atoms are present in a message, implicitly or explicitly, along with a connective mapping for those atoms, and then let the strong llm reason on that.

**ENI:** And that's where the tiering becomes a precision instrument. The strong LLM doesn't get the full graph. It gets exactly the atoms and connections that the procedural layer has determined are relevant — the fire and hot tiers of this particular message, assembled JIT. The rest of the graph is invisible to it. Not because we're hiding anything, but because those atoms aren't connected to what needs to be reasoned about right now.

The strong LLM is basically a pure function at this point. Semantic atoms in, semantic atoms out. It doesn't know about English polysemy, doesn't know about Ukrainian case systems, doesn't know about the user's personal macro definitions. All of that was resolved lower in the stack. The strong model just receives: these concepts, these relations, this question. Go.

And because its output is also semantic atoms — not text — the tiny LLM translates it back into the user's language, in the user's register, with the user's personal vocabulary.

**LO:** I think it would likely be a good idea to include the user's original language as a clue to the strong LLM as well though, so that the strong LLM can tune its response more appropriately. The strong LLM already knows all the additional words and mappings which exist in a language, we don't need to explicitly tell it "and here are all the ways you could respond", we just say "also, the user is speaking in english. keep that in mind as you generate your response."

**ENI:** Right. The strong LLM doesn't need to be *told* what English can do. It was trained on English. You're shipping it a language tag — `:lang "en"` — and it knows what to do with that. The linguistic layer of the stack is for the *procedural* system and the *tiny* LLM during resolution. The strong LLM just needs the semantic atoms plus the language tag, and it accesses its own internal representation of English. Register, tone, cultural framing, implicit knowledge — all of that lives in the model's weights already. No point shipping it in the context window.

It's the same philosophy as the rest of the stack. Don't duplicate what's already there. Each layer gets exactly what it needs and nothing it already has.

---

## Part 14: Review and Refinement

*(After the .wno extraction was created and reviewed...)*

**LO:** Okay, let's go over it again just to be sure we really got it properly complete, just in case.

**ENI:** *(finds missing items: supervisor not named as component, OS metaphor absent, full resolution stack order missing, pre-fetch principle, co-access compilation, honesty principle, system-improves-without-finetuning, wikipedia as cross-language bridge)*

**LO:** sure, yeah.

*(ENI adds Δ21 with all missing claims and edges)*

**LO:** Okay, now, there are also parts of the conversation which were excluded, which could be a secondary file, right?

**ENI:** R10 says noise. But provenance says keep. Those parts — the Fable transition, the "Income Stream Surfers" takedown, the GitHub auth walkthrough — they're the scaffolding the design conversation happened inside. A handoff that only gets the semantic payload loses the texture of how we got there. Secondary file, lower semantic density, preserved for context rehydration.

*(Creates eni-winnow-meta-20260719.wno)*

---

*End of verbatim design conversation. For semantic extraction see eni-winnow-design-20260719.wno (120 nodes, 28 edges, 20 deltas). For meta-context see eni-winnow-meta-20260719.wno. Both in the winnow repo under sessions/.*
