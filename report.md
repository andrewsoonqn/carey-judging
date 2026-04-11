#2526s2/nst2062

# NST Carey Evaluation Results

**How can we improve current AI chatbots to better emotionally support caregivers through higher conversational diversity?**

By Veda, Aishwarya, Hazel and Andrew

## Objective

This milestone investigates whether current AI chatbots can better emotionally support caregivers by improving **conversational diversity**. For this project, conversational diversity refers to the variation in how a chatbot structures its responses and uses different conversational strategies across a dialogue, such as expressing understanding, probing, and offering suggestions.

Our core question is:

**How can we improve current AI chatbots to better emotionally support caregivers through higher conversational diversity?**

## Background And Motivation

Our Milestone 1 was positively received for its strong conceptual frameworks. In particular, the project was recognised for carefully navigating ambiguity around actual or simulated empathy and conversational design, and for grounding these ideas in a clear methodological approach.

At the same time, the main area for improvement was that our scope remained too broad. While Milestone 1 valued breadth, Milestone 2 required us to go deeper and move from a collection of ideas to a focused, testable system at the smallest dimensions.

Another key takeaway was the need to better identify specific failure modes in current systems. Rather than stating broadly that chatbots lack empathy, we needed to narrow to specific features of simulated empathy in conversations. This led us towards the scope of existing chatbots' ineffectiveness at probing for more context or diversifying responses.

We were also encouraged to make our definitions more concrete. Concepts such as empathy and emotional sensitivity needed to be translated into observable and measurable behaviours in our context. The risk of performative empathy was also raised, where responses sound caring but do not meaningfully improve support. This highlighted the importance of grounding our work in evaluation rather than relying on surface-level indicators.

Moving forward with this feedback, we adopted a more focused, evaluation-driven approach. This involved defining clear quantifiable success metrics that are both meaningful and robust, while acknowledging the fluid, contextual, and perceptual nature of human interaction.

We also tested the Carey model using Gemini 2.5 Flash and quickly observed that the conversations did not feel convincingly human-like. Each response followed a rigid three-paragraph structure: validating, elaborating, and ending with "I am here to listen." While consistent, this created an artificial conversational pattern that diverged from how humans naturally communicate.

Real human conversations are far more dynamic and context-sensitive. They often involve interruptions, follow-up questions, clarifications, and shifts in tone depending on the situation. The Carey model, however, tended to produce long, fully formed responses even when insufficient context was provided, without first probing the user for more information. This lack of conversational adaptability reduced the sense of authenticity and made interactions feel scripted rather than organic.

LLM-generated conversations systematically differ from human ones in structure and variability. Human-like dialogue requires diversity in turn-taking, response length, and conversational style (Lin et al., 2024). Prior research also suggests that chatbot interactions characterised by person-centered communication emphasising empathy, concern, and tailored communication styles yield more positive outcomes (Heyn et al., 2023).

Motivated by this, we focused our Milestone 2 on improving diversity in conversational structure. Instead of uniform responses, we aimed to vary how the system responds, sometimes asking questions, sometimes giving brief acknowledgements, and other times offering more detailed reflections, to create more natural and human-like interactions.

## Approach

### Benchmark Selection

In developing an evaluation framework for our AI chatbot, we first examined existing evaluation criteria, particularly Carey's framework.

![Snippet of Carey's evaluation criteria for diversity](64d90c59aab88946e2c9ea5bdaa2a4c8.png)

_Fig 1: Snippet of Carey's evaluation criteria for diversity_

Carey's criteria were useful as an initial reference point, especially in highlighting the importance of diversity in chatbot responses. However, as we began applying them to our own outputs, we found that the criteria were largely qualitative and lacked clear definitions. This made them difficult to apply consistently or use for meaningful comparison across different model responses.

Through our initial trials with Carey's framework, we also realised that its concept of diversity focused mainly on variation in content. In practice, we observed that this was only one part of what made a conversation feel natural. The way a response was structured also mattered. Responses that varied between showing empathy, asking follow-up questions, and offering suggestions felt more human-like than responses that repeated the same format. This observation highlighted a gap between existing evaluation criteria and what we wanted to measure in our project.

Before deciding to design our own metrics, we explored established benchmarks such as ESC-Eval and EmoBench (Zhao et al., 2024). ESC-Eval is designed to evaluate how effectively large language models provide emotional support in conversations. It uses a role-playing agent to simulate dialogues based on predefined personas, which are then analysed. EmoBench is a broader benchmark that evaluates emotional intelligence, including both understanding and application of emotions in complex scenarios.

After closer inspection and some initial testing, we found that ESC-Eval was more suitable for our project setup. EmoBench was less applicable because much of its format is closer to emotional-intelligence question answering than to open-ended chatbot interaction. By contrast, ESC-Eval gave us three things we needed: a simulated conversation partner, reusable role cards, and a post hoc tagging step. The role cards were especially useful because they let us run the same evaluation procedure across different caregiver situations instead of testing only one generic conversation setup. This was also feasible within our project timeline and gave us room to iterate on the setup over time. We therefore adopted ESC-Eval's general methodology, especially the use of role cards, simulated conversations, and label-based analysis. At the same time, we found that neither ESC-Eval nor EmoBench provided evaluation metrics that directly captured the type of diversity we were interested in. This reinforced our decision to develop our own criteria.

### Scope Narrowing

We then returned to the idea of diversity and explored what it could mean in the context of chatbot responses. In our early brainstorming, we identified several possible dimensions. These included diversity in adapting responses to different concerns, diversity in tailoring responses to cultural context, and diversity in response structure.

However, as we progressed, we recognised practical constraints in time and resources. We also found that some dimensions, such as cultural adaptation, were more difficult to measure reliably. Based on this, we made a deliberate decision to narrow our focus to diversity in answer structure. This was easier to operationalise and quantify, and our earlier testing suggested that it had a noticeable impact on how natural the conversation felt. In our pilot interactions, repetitive structure was not just aesthetically repetitive; it made the chatbot feel rigid, less human, and less immersive as a conversation partner. This was one of the main reasons structural diversity became worth optimising in the first place. Research in conversational psychology also supports the idea that effective dialogue involves variation in conversational moves, such as listening, probing, and advising (Ward & Wataru Tsukahara, 2003).

Another question we had to resolve was whether diversity should be measured only within a single conversation or also across different conversations. We concluded that both matter. A system can vary its strategies within one dialogue while still falling back on the same overall structure across cases, or it can vary across cases while remaining repetitive within each individual interaction. This is why our later evaluation framework includes metrics that capture both levels.

To further ground our evaluation in a relevant context, we referred to the Singapore Medical Council Ethical Code and Ethical Guidelines (_Singapore Medical Council_, 2016). This helped us identify important considerations in caregiver-style communication, such as empathy, appropriateness, and responsiveness to user needs. These considerations informed how we interpreted and applied the idea of diversity in a healthcare-oriented chatbot setting.

### Why We Chose Fine-Tuning

Before selecting our implementation approach, we considered three candidate methods: fine-tuning on caregiver-specific data, adding a separate emotion-detection layer, and using Chain of Empathy (CoE) prompting. We ultimately chose fine-tuning because it was the most direct way to change the model's response behaviour at the level we cared about, namely conversational structure across multi-turn dialogue.

Our intuition was that a general-purpose language model is trained to perform reasonably well across many tasks, and so tends to fall back on broadly useful, average response patterns. For our project, however, being generally competent was not enough. We wanted the model to become better at one specific task: producing more varied and contextually appropriate supportive responses in caregiver-style dialogue. Fine-tuning offered a way to push the model away from a generic default style and toward the particular patterns we wanted it to learn.

In particular, we expected fine-tuning to help the model pick up recurring features of how supportive conversations unfold: when it is better to probe, when to prioritise understanding, and how to vary response structure across contexts instead of repeating a single template. We do not explicitly hard-code these rules into generation. Rather, the idea is that by repeatedly exposing the model to examples with these patterns, fine-tuning can shift what the model treats as salient and what kinds of responses it tends to produce by default.

This was also the most practical option within our project scope. An emotion-detection layer would have introduced an additional component whose own performance would need to be designed and validated, while CoE would mainly affect prompting behaviour rather than the underlying response style of the model itself. Fine-tuning gave us a cleaner intervention to compare against a baseline, since we could change the model's behaviour through training while keeping the evaluation setup largely fixed.

### Gold-Standard Features

The training setup was therefore designed around the conversational features we wanted the model to learn as a gold standard for this task.

First, supportive dialogue should not feel monotonous. A good response pattern should shift across turns instead of relying on one fixed structure throughout the conversation. In our context, this means moving between different conversational strategies such as probing, reflecting, validating, and suggesting, rather than repeating the same supportive template each time.

Second, these shifts should be context-sensitive rather than random. The model should not merely display more strategies; it should learn when it is appropriate to probe, when to reflect understanding, and when to move toward suggestions or action. Clarification under uncertainty is part of this broader feature: if the user's situation is underspecified, the model should try to understand what is going on before moving into advice.

Of these two features, the current training setup represents the first more directly, since we explicitly discourage repetitive templates and record turn-level strategies. The second is also represented, especially through underspecified user turns and first-turn probing requirements, but it is captured less completely. Our data encourages clarification and multiple strategies, yet the exact logic of when to switch between them across later turns remains more implicit than explicit.

### Training Setup

Our training setup follows from these target features. The training dataset contains full conversation transcripts used for fine-tuning. To generate this dataset, we first defined caregiver-oriented scenarios and structural constraints ourselves, then used an LLM to produce conversation drafts, and finally reviewed these outputs before including them.

Because context-sensitive sequencing was one of our core target behaviours, the user is framed as an informal caregiver and the initial user message is kept slightly underspecified so that clarification and probing feel natural. The first assistant response is required to probe, clarify, or reflect-probe before giving advice, rather than defaulting to a fixed structure such as "validate, normalize, open question."

Because we also wanted the model to learn non-monotonous but realistic support, each conversation focuses on a single caregiving issue, the tone is constrained to be supportive but not overly therapist-like, and crisis, diagnosis, or clinical claims are excluded. Each training conversation consists of 3 user turns and 3 assistant turns, and is stored in a structured JSON format capturing elements such as scenario, care context, and the strategies used in each assistant response.

As we iterated on the dataset, we also made the generation prompt more comprehensive. Rather than asking only for generally supportive dialogue, we added clearer instructions about caregiver identity, the number of turns, first-turn strategy, safety boundaries, and structured output fields. The purpose of this refinement was to reduce noisy or overly generic generations and to make the training examples more consistent with the specific conversational patterns we wanted the model to learn. In that sense, prompt refinement functioned as a robustness measure for dataset generation: it narrowed the space of possible outputs so that fine-tuning was driven by more controlled and interpretable examples.

Overall, the goal of this setup was to engineer a training distribution in which the model repeatedly sees the kinds of conversational patterns we wanted it to internalise: variation in response structure, and more appropriate sequencing between understanding and action, including clarification when context is missing.

### Training Objective And Constraints

The fine-tuning uses supervised fine-tuning (SFT) with the standard causal language modelling objective: the model is trained to predict the next token in each training conversation. No custom reward signal or reinforcement step is involved. The training data is formatted as multi-turn chat transcripts, and the loss is computed over the full sequence so that the model learns to reproduce the conversational patterns present in the dataset.

To make fine-tuning practical on limited hardware, we use Low-Rank Adaptation (LoRA) rather than updating all model weights. LoRA inserts small trainable matrices into the model's attention layers while keeping the original weights frozen. In our setup, the adapter targets the query and value projection matrices (`q_proj`, `v_proj`) with rank 16, scaling factor (alpha) 32, and dropout 0.05. The base model is also loaded in 4-bit precision using NF4 quantisation with double quantisation enabled, which reduces memory usage enough to fine-tune on consumer-grade hardware.

The training ran for a single epoch with a maximum of 50 gradient steps, a learning rate of 2 × 10⁻⁴, and an effective batch size of 4 (per-device batch size of 1 with 4 gradient accumulation steps). The maximum sequence length was 512 tokens.

Relative to the baseline, the only change introduced by fine-tuning is the LoRA adapter. The base model weights are identical between Qwen Fine-Tuned and Qwen Untuned; the fine-tuned variant simply loads an additional set of low-rank adapter weights on top of the frozen base. This makes the comparison between the two Qwen variants a controlled test of whether the adapter, trained on our diversity-oriented dataset, shifts the model's conversational behaviour in the intended direction.

## Evaluation Criteria

At the same time, we recognise that qualitative aspects, such as conversational naturalness and appropriateness, are important in evaluating dialogue systems. Instead of excluding them, we used these ideas to guide the design of our quantitative metrics by translating them into measurable indicators. These metrics can be computed efficiently using a programme, allowing us to analyse multiple conversations consistently without introducing subjective bias from manual grading. While this approach does not directly measure qualitative experience, we argue that the selected quantitative metrics serve as reasonable proxies for the underlying qualitative concepts.

Qualitative evaluation can also be understood as the human process of interpreting, summarising, and weighing different aspects of a conversation to form an overall judgement. While it may not always be expressed numerically, it still relies on identifying underlying conversational patterns. From this perspective, qualitative assessment is not separate from quantitative reasoning, but a different way of interpreting it. This guided our approach as we aimed to make these implicit judgements more explicit and measurable.

Through this process of refinement, we narrowed our framework down to three main metrics. These metrics were designed to capture both variation within a single conversation and variation across different conversations.

| Dimension | Definition                                                                                                                                                                                                                                                                                                                                                              | Metrics                                                                                                                                                                                                                                                                                                            |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Diversity | Diversity is defined as the degree of variation in both the structure and content of responses throughout a dialogue in a healthcare context. It reflects the chatbot's ability to employ a range of conversational strategies, such as demonstrating empathy, engaging in probing, and providing actionable guidance, rather than relying on a fixed response pattern. | **Strategy Variety (Count of Unique Strategies):** Number of distinct conversational strategies used across the entire dialogue. This measures the range of strategies employed, for example probing, reflection, and suggestion.                                                                                  |
| Diversity | Same as above.                                                                                                                                                                                                                                                                                                                                                          | **Strategy Distribution (%) - Within a conversation:** Percentage share of each strategy across all turns in the dialogue. This measures how evenly strategies are used by calculating the proportion of total responses attributed to each strategy, for example 60% probing, 20% reflection, and 20% suggestion. |
| Diversity | Same as above.                                                                                                                                                                                                                                                                                                                                                          | **Structural Variation (%) - Across conversations:** Percentage of conversations that differ in overall structure, for example whether all conversations follow the same Probe-Probe-Suggest pattern.                                                                                                              |

Overall, our framework evaluates the diversity and richness of responses in a healthcare-based conversational setting. We define diversity not just in terms of content, but in terms of how responses are structured across a dialogue. A more effective chatbot, in this context, is one that varies its response strategies, for example by combining empathy, clarification, probing questions, and solution-oriented guidance rather than relying on a fixed pattern.

## Evaluation Method

The main reported evaluation used an ESC-Eval-inspired pipeline run through the OpenAI API because it was more practical for batch testing.

In the main evaluation, we compared three chatbot systems acting as the `friend`, or system under test:

- a baseline `gpt-5.4-mini` chatbot
- an untuned `Qwen2.5-7B-Instruct` chatbot
- a fine-tuned `Qwen2.5-7B-Instruct` chatbot

Although the evaluation pipeline involved three model roles, the `friend` role was instantiated by three different chatbot systems. The `friend` is the chatbot being evaluated. The `victim` is a standardised simulator that receives a role card and plays the conversation partner. The `tagger` is a separate model that labels only the `friend` turns after the conversation is generated. In our setup, the `victim` was `gpt-5.4-mini`, while the `tagger` was `gpt-5.4-nano`.

Each evaluation run begins with a role card, which specifies the scenario or caregiver persona for the simulated conversation. These role cards form a separate evaluation dataset: they are used to standardise the testing situations, not to train the model. A role card is given to the `victim`, which then interacts with the `friend` across a fixed dialogue. Using a set of role cards rather than a single prompt also makes the evaluation less tied to one narrow interaction pattern and therefore somewhat more robust across cases, even though it remains a simulated benchmark. The raw transcript is stored first. After that, the `tagger` labels each `friend` turn as a separate derived artifact. For every `friend` turn, the tagger assigns one `structure` label, one `primary_strategy` label, and optional `secondary_strategies` when a turn clearly combines techniques.

We used two kinds of labels. The structure labels describe the overall shape of the turn: `question`, `reflection`, `suggestion`, or `hybrid`. The strategy labels describe the main conversational move, including `probe`, `reflect`, `validate`, `reframe`, `suggest`, `plan`, and `support`.

Our analysis is then computed from these labels rather than from raw conversation text alone. After tagging, the per-turn labels are flattened into analysis tables, from which we compute strategy variety, strategy distribution within a conversation, and structural variation across conversations. This gives us a consistent way to compare how differently the three systems behave across the same set of simulated caregiver scenarios.

We referenced the ESC-Eval setup in designing this method, particularly its use of role-based interactions, a standardised simulator, and label-based analysis. We adopted the methodology, but changed the downstream criteria to focus specifically on conversational diversity.

Using language models in this way also served a practical methodological purpose. LLM generation allowed us to scale both scenario creation and transcript production, while the simulator-tagger setup allowed us to evaluate many conversations under the same procedure. However, this also means our measurement depends on the behaviour of the simulator and tagger models, so the results should be interpreted as benchmarked performance within this pipeline rather than as a direct measure of real human caregiver support.

Our original evaluation plan included pretest and posttest interviews with Singapore-based caregivers, which would have grounded our metrics in the lived experience of the population we aimed to support. However, within the constraints of this project, we did not have sufficient time or outreach access to recruit and interview a meaningful number of caregivers. Rather than conducting interviews with too few participants to draw reliable conclusions, we chose to rely entirely on the LLM-based evaluation pipeline described above. We acknowledge this as a trade-off: the simulated approach gives us reproducibility and scale, but it cannot substitute for direct caregiver feedback on whether increased diversity actually translates to a more supportive conversational experience. Incorporating real caregiver perspectives remains an important direction for future validation.

### Reproducibility

To keep the evaluation reproducible, we treat the pipeline as a sequence of separate stages rather than one opaque batch process. Each role card first produces a raw conversation transcript. That transcript is then tagged in a separate step, and only afterward are dataset-level metrics computed from the stored tags. In other words, simulation and tagging happen per conversation, while analysis happens later over the completed set. This separation matters because it allows us to rerun or inspect one stage without overwriting the earlier source artifacts.

We also separate raw artifacts from derived artifacts. The raw artifacts are the role-card set actually used for the run, the relevant prompt versions, the model identities, and the saved transcripts. The derived artifacts are the per-turn tags and the aggregate metric tables computed from those transcripts. This means that if we revise the taxonomy or analysis code later, we can recompute the derived outputs without losing the original conversations that were generated.

At the run level, reproducibility depends on versioning and stable identifiers. We keep the role-card set, victim prompt template, friend configuration, tagger taxonomy, and model choices fixed within a run, and we store stable IDs such as `run_id`, `role_card_id`, and `conversation_id` so that each artifact can be traced back to the exact configuration that produced it. This also makes the pipeline resumable: failed or incomplete conversations can be rerun without corrupting completed ones, and later comparisons across runs can be tied to explicit prompt, model, and taxonomy versions rather than informal notes.

### Model Selection Rationale

The three-model comparison was designed to isolate the effect of fine-tuning from differences in model architecture and scale.

**Qwen2.5-7B-Instruct** was chosen as the base model for fine-tuning because it is an open-weight, instruction-tuned model that can be adapted and inspected locally. Open weights are important for this project because fine-tuning a closed API model is either impossible or opaque: we would not be able to verify what changed or reproduce the intervention independently. The 7-billion-parameter size was a practical choice — large enough to produce coherent multi-turn dialogue, but small enough to fine-tune with LoRA and 4-bit quantisation on consumer hardware within our project timeline. Qwen2.5-Instruct also has competitive instruction-following performance for its size class, making it a reasonable starting point for a task that depends on the model's ability to follow structured conversational patterns.

**GPT-5.4-mini** was included as a strong commercial baseline. It represents the kind of general-purpose model that most users would interact with in practice. Comparing our fine-tuned open-weight model against a larger, closed-weight frontier model tests whether targeted fine-tuning on a specific task can outperform a more capable but general-purpose system on that same task. GPT-5.4-mini also served as the `victim` model (the simulated caregiver user), since it is capable enough to produce contextually appropriate role-played responses that give each `friend` model a realistic conversation partner.

**Qwen2.5-7B-Instruct (untuned)** was included as an architectural control. Without it, any difference between Qwen Fine-Tuned and OpenAI could reflect either the fine-tuning intervention or inherent differences between the Qwen and GPT model families. By comparing the fine-tuned model against the same base model without the adapter, we can attribute differences between the two Qwen variants specifically to the fine-tuning rather than to the architecture.

**GPT-5.4-nano** was used as the tagger model. Tagging is a constrained classification task — assigning labels from a fixed taxonomy to individual turns — which does not require the full generative capacity of a larger model. Using a smaller, cheaper model for this role kept API costs manageable while still producing consistent labels across the full evaluation set.

### Testing Limitations

Several limitations of the evaluation pipeline itself should be noted separately from the broader project limitations discussed later.

**No inter-rater reliability check.** All strategy and structure labels were assigned by a single LLM tagger. We did not perform human annotation of a sample subset to measure agreement between the tagger and human judgement. The tagger may have systematic biases — for instance, it might interpret shorter Qwen responses differently from longer GPT responses, or tend toward certain labels regardless of the actual conversational move.

**Victim–friend interaction effects.** The victim model may steer conversations differently depending on the friend's responses. If one friend model produces shorter, more probing responses, the victim may provide more detail in return, creating different conversation dynamics. Our metrics attribute all variation to the friend model, but some of it may arise from the interaction between the friend and victim rather than from the friend alone.

**No statistical significance testing.** The reported metrics are point estimates computed over 57–100 conversations per model. We did not apply bootstrap confidence intervals, permutation tests, or other statistical procedures to determine whether the observed differences are likely to hold under resampling. The relative ordering of the three models is consistent across metrics, but the magnitude of the differences has not been formally tested.

**Single evaluation run per model.** Each model was evaluated once over the role-card set. Without repeated runs, we cannot estimate the variance of the aggregate metrics or determine whether the observed differences would be stable across independent runs with different random seeds or conversation orderings.

**Tagger–friend model family overlap.** The tagger (GPT-5.4-nano) belongs to the same model family as the baseline friend (GPT-5.4-mini) and the victim (GPT-5.4-mini). This creates a potential calibration asymmetry: the tagger may be more accurately calibrated for labelling responses generated by models from its own family than for labelling Qwen-generated responses, which could introduce a systematic bias in the tag distributions.

<!-- Pending: pipeline diagram, repo reference, notebook, adapt for 100 cases -->

## Measurement Framework

To clarify what our evaluation is actually doing, it is useful to distinguish between the underlying concept we care about and the measurable signals we use to approximate it.

### Representation

Our experiment represents caregiver support through simulated role-based conversations between AI agents. It also represents conversational diversity through a limited set of observable conversational strategies, such as probing, reflection, support, and suggestion. This is a deliberate modelling choice. It allows us to study one specific aspect of emotionally supportive dialogue, but it also narrows the phenomenon we are evaluating.

This means our setup does not capture the full range of what may matter in real caregiver support. For example, it does not directly represent cultural sensitivity, long-term trust, timing, pacing, or whether support is genuinely helpful from a human user's perspective. Our role cards are also abstractions of caregiver experiences rather than direct representations of real clinical cases.

### Representation Part II: Model-Level Intuition

There is also a second sense in which representation matters in this project: the internal representations used by the model itself. Our motivation for fine-tuning is that supportive caregiver dialogue depends not only on explicit instructions, but also on what the model notices and how it organises the task internally. A general-purpose model may recognise many relevant cues, but still respond in a generic, averaged way because its default behaviour is shaped by broad training objectives rather than this specific conversational setting.

Fine-tuning is therefore intended to shift the model toward a different internal organisation of the task. In our case, this means making cues such as ambiguity, emotional burden, and the need for clarification more behaviourally important during generation, while also biasing the model toward a wider range of conversational moves. We do not claim direct evidence that fine-tuning changed one precise internal representation. Rather, this is our theoretical intuition for why fine-tuning is a plausible intervention: it may alter both what features are effectively foregrounded and how those features are mapped to supportive responses.

### Formal Object And Measurement

The formal object we measure is not emotional support in general. More precisely, we measure the **structural diversity of supportive conversational behaviour** within and across dialogues.

We operationalise this through three quantitative metrics:

- strategy variety
- strategy distribution within a conversation
- structural variation across conversations

These metrics allow us to convert an abstract idea such as conversational diversity into something that can be compared systematically across model outputs. However, they remain proxies rather than direct measurements of emotional support quality.

To compare runs at the aggregate level, we also compute two composite indicators from the per-conversation metrics above.

**Strategy entropy** is the Shannon entropy over the run-wide strategy frequency distribution:

$$H = -\sum_{i=1}^{k} p_i \, \log_2(p_i)$$

where $p_i$ is the proportion of all friend turns in a run that were tagged with strategy $i$, and $k$ is the number of distinct strategies observed. Entropy is maximised when every strategy is used equally often and minimised when the model relies on a single strategy. It therefore captures how evenly a model distributes its conversational moves across the full set of available strategies.

**Diversity score** is a composite metric that combines several of the per-conversation indicators into a single comparable value:

$$D = H + \bar{U} - \frac{\overline{S\%}}{100} - R_{\text{all-same}}$$

| Symbol | Meaning |
|--------|---------|
| $H$ | Strategy entropy (defined above) |
| $\bar{U}$ | Mean number of unique primary strategies per conversation |
| $\overline{S\%}$ | Average same-primary-strategy percentage across conversations (divided by 100 to normalise to 0–1) |
| $R_{\text{all-same}}$ | Share of conversations in which every friend turn used the same primary strategy |

The first two terms reward variety (higher entropy, more unique strategies), while the last two penalise repetition (high same-strategy rate, many monotonic conversations). A higher diversity score therefore indicates a model that varies its strategy both across conversations and within each conversation.

### Evidence

The evidence in our experiment consists of the generated conversations, the strategy labels assigned to assistant responses, and the aggregate metric values computed from these outputs. These observations allow us to make claims about whether one model produces more varied conversational structures than another under our framework.

Importantly, this evidence supports claims about increased structural diversity more directly than claims about improved emotional support. In other words, if the trained model scores better on our metrics, we can more confidently conclude that it is more diverse under our definition, but only indirectly that it is more emotionally supportive.

### Intervention

Our main intervention is the design of a diversity-oriented dataset and the corresponding fine-tuning process. This intervention is intended to encourage the model to use a wider range of supportive conversational strategies rather than relying on a fixed template.

We then test whether this intervention changes the measured outputs relative to the baseline model. In addition, our shift from shorter 3-turn conversations to longer 10-turn conversations can also be understood as an intervention on the evaluation setup itself. This matters because longer conversations may reveal diversity more clearly, but they may also change what the metrics are able to capture. As a result, we need to be careful when making causal claims about what caused any observed improvement.

### Failure Modes

This framework highlights two kinds of failure modes: the baseline failure modes that motivated the intervention, and the new failure modes that may appear after fine-tuning.

Before fine-tuning, the main failure mode was structural monotony. The model could rely too heavily on one default response pattern, producing supportive-sounding but repetitive dialogue. In practice, this appeared as long, rigidly structured responses, insufficient clarification before advice, and limited movement between conversational strategies across turns. These failures made the chatbot feel less natural and less responsive, even when the individual responses were not obviously wrong.

After fine-tuning, a different set of risks emerges. Once conversational diversity becomes an optimisation target, the model may learn to game the metric by alternating between strategies more often without becoming genuinely more supportive. This could take the form of random or mechanical diversity, where the model switches strategy for the sake of variation rather than because the context calls for it. In that case, the system may look more diverse under our labels while becoming less coherent or less appropriate as a conversation partner.

Related to this, the model may display only superficial diversity. It may vary the structure of its responses while still offering repetitive, shallow, or mistimed support. If probing is implicitly rewarded, the model may also overuse emotionally probing responses even in situations where reassurance, brevity, or direct guidance would be more appropriate. This would create higher measured diversity while making the interaction less natural.

There are also longer-term generalisation risks. The model may overfit to our role cards or assumptions about caregivers rather than learning a form of support that generalises to real users. This is especially relevant because our personas are simplified representations rather than grounded clinical profiles. More broadly, optimisation may change the meaning of the metric itself. Before optimisation, conversational diversity may function as a useful diagnostic indicator of naturalness. After optimisation, it may become a performative behaviour produced for the sake of scoring well, weakening the link between the metric and the underlying quality we originally cared about.

## Results

### Iteration 1

The first iteration was intended to check whether the model worked with the role cards and whether the setup could run end to end. We used 3-turn conversations.

The model worked, but we found very little improvement or difference in the metrics. We considered that this might be because the conversations were too short, making it difficult to assess variability in strategies across turns.

### Iteration 2

In the second iteration, we increased the length of the conversations to 10 turns. Each of the three systems was evaluated over 100 role-card scenarios (57 for Qwen Untuned due to an incomplete batch), producing 1000 friend turns per full run. The results reported here are preliminary: the Qwen Untuned run covers 57 of the planned 100 scenarios, so its numbers may shift once the remaining conversations are processed. The patterns observed so far are consistent enough to report, but final values should be confirmed against the complete dataset.

The table below summarises the aggregate metrics across all three systems.

| Metric | OpenAI | Qwen Fine-Tuned | Qwen Untuned (partial) |
|--------|--------|----------------|-------------|
| Avg same-primary strategy (%) | 53.40 | 47.10 | 52.81 |
| Mean unique strategies per conversation | 3.50 | 3.99 | 3.49 |
| Mean strategy switches per conversation | 4.62 | 5.60 | 4.67 |
| Strategy entropy | 2.163 | 2.201 | 2.073 |
| Diversity score | 5.129 | 5.720 | 5.036 |

The fine-tuned Qwen model scores highest on all five indicators. Importantly, the inclusion of the untuned Qwen model serves as a control for model architecture: any difference between Qwen Fine-Tuned and OpenAI could reflect either the fine-tuning intervention or inherent differences between the Qwen and GPT architectures. By comparing Qwen Fine-Tuned against both Qwen Untuned (same architecture, no fine-tuning) and OpenAI (different architecture, no fine-tuning), we can better isolate which improvements are attributable to the fine-tuning itself rather than to the base model.

The subsections below examine the data from four different angles to understand where the improvement comes from and what it means.

#### Strategy variation and monotony (within conversation)

A key goal of fine-tuning was to reduce monotonous response patterns within individual conversations. Three per-conversation metrics bear on this directly.

**Unique strategies per conversation.** On average, Qwen Fine-Tuned uses 3.99 distinct primary strategies per conversation out of a possible 7, compared with 3.50 for OpenAI and 3.49 for Qwen Untuned. This means the fine-tuned model draws from a wider repertoire in each individual dialogue rather than relying on a narrow subset.

**Strategy switches per conversation.** Qwen Fine-Tuned switches between strategies 5.60 times per conversation on average, compared with 4.62 for OpenAI and 4.67 for Qwen Untuned. A higher switch count indicates that the model is not simply using more strategies in isolation but is actively transitioning between them as the conversation develops.

**Same-primary-strategy rate.** The proportion of turns in a conversation that repeat the single most common strategy drops to 47.1% for Qwen Fine-Tuned, compared with 53.4% for OpenAI and 52.81% for Qwen Untuned. A lower rate means the dominant strategy is less dominant, leaving more room for other strategies to appear.

These differences are not only visible in the means. The per-conversation distributions (Figure 4) reveal that Qwen Fine-Tuned's improvement is consistent across conversations rather than driven by a few outliers. The interquartile range for unique strategies is shifted upward relative to both baselines, and the same-strategy percentage distribution is shifted downward. The box plots also show that Qwen Fine-Tuned's same-strategy percentage has a tighter spread than the baselines, meaning the model is not only less repetitive on average but more consistently so — there are fewer conversations that revert to a single dominant strategy. In other words, most conversations produced by the fine-tuned model are individually more varied, not just the average.

#### Turn-by-turn trends (across conversations)

Examining how strategy usage evolves from the first turn to the last reveals patterns that the aggregate numbers above cannot show. Figure 3 plots the share of each strategy at every turn position for all three models.

Most strategies follow broadly similar trajectories across the three systems. `Validate` spikes at turn 2 in all three models (79% for OpenAI, 53% for Qwen Fine-Tuned, 56% for Qwen Untuned) before declining steadily — a shared reflex of acknowledging the user's first substantive message. `Reflect` drops sharply after turn 1 across the board. `Support` rises through the conversation for both Qwen models while remaining flatter for OpenAI, a pattern that appears to reflect architectural differences between the Qwen and GPT families rather than fine-tuning. This is where the Qwen Untuned baseline is especially useful: where the two Qwen models track each other closely on a strategy, the difference from OpenAI is more likely an artefact of the base model than a product of fine-tuning. Two strategies, however, show clear divergences that can be attributed to the fine-tuning intervention.

**Plan: significantly lower for Qwen Fine-Tuned.** The `plan` chart in Figure 3 shows that OpenAI uses the `plan` strategy at a notably higher and more erratic rate across the conversation (fluctuating between 3% and 11%), and Qwen Untuned follows a similar if slightly lower trajectory (2–9%). Qwen Fine-Tuned, by contrast, stays consistently low at 2–4% throughout. Since both baseline models use `plan` at higher rates and the untuned Qwen model is closer to OpenAI than to its fine-tuned counterpart, this suppression appears to be an effect of fine-tuning: the training data favoured strategies like probing and reflecting over action planning, and the model appears to have down-weighted `plan` accordingly.

**Suggest: Qwen Fine-Tuned markedly lower than both baselines.** The most striking trend difference is in `suggest`. OpenAI's suggestion usage climbs steeply from near 0% at turn 1 to approximately 50% by turn 5, then plateaus at 40–48% for the remainder of the conversation. Qwen Untuned is also relatively suggestion-heavy, rising to 25–39% from the mid-turns onward. Qwen Fine-Tuned, however, stays substantially lower than both, rising gradually from 3% to around 19–22%. This is not simply a Qwen architectural trait — Qwen Untuned's suggest rates are much closer to OpenAI's than to the fine-tuned model's — so the reduction appears to be a direct consequence of fine-tuning. Rather than converging on advice-giving as the default late-turn behaviour, the fine-tuned model distributes its action-oriented responses more evenly between `suggest` and `support`, maintaining a more balanced conversational posture.

**First-turn probing.** At turn 1, Qwen Fine-Tuned uses the `probe` strategy 33% of the time, compared with 6% for OpenAI and 21% for Qwen Untuned. This directly reflects the training data, which required the first assistant response to probe or clarify before giving advice. The fine-tuned model appears to have internalised this pattern: rather than immediately validating or suggesting, it asks questions first. Notably, it continues to probe at meaningful rates (5–8%) through turns 7–10, whereas OpenAI drops to 0–3% after the first few turns. The Qwen Untuned model starts with a moderate probe rate (21%) but drops to near zero after turn 1, suggesting that the base Qwen architecture has some inclination toward initial probing, but that fine-tuning substantially amplified and sustained this behaviour.

#### Lexical and strategic diversity

The entropy and diversity scores provide a single-number summary of how evenly a model distributes its turns across the available strategies.

**Strategy entropy.** Qwen Fine-Tuned achieves an entropy of 2.201, compared with 2.163 for OpenAI and 2.073 for Qwen Untuned. For context, the maximum possible entropy for 7 strategies (a perfectly uniform distribution) is approximately 2.807. All three models therefore operate in the 74–78% range of maximum entropy. The gap between the fine-tuned model and the baselines is real but modest, suggesting that the improvement in diversity is more about shifting the balance of strategies than achieving a radically different distribution.

**Strategy concentration.** A complementary way to see this is through strategy concentration, as shown in Figure 1. OpenAI concentrates 66.6% of all turns in just two strategies: `suggest` (32.4%) and `validate` (34.2%). Qwen Untuned is similarly top-heavy, with `support` (31.75%) and `validate` (31.58%) accounting for 63.3%. Qwen Fine-Tuned, by contrast, distributes its turns more broadly. While `validate` (40.4%) remains the single most common strategy, `support` (23.4%), `suggest` (16.0%), and `probe` (10.0%) each carry meaningful weight, and no pair of strategies accounts for more than 64% of turns. Figure 1 also highlights that `reframe` remains largely unused by all three models (below 1%), suggesting that this strategy is either difficult for the models to produce or that the tagger rarely assigns it — either way, the effective strategy space in practice is closer to 6 than 7.

**Active versus passive balance.** Grouping strategies into active (`plan`, `suggest`, `support`, `validate`) and passive (`probe`, `reflect`) categories makes the distributional shift more visible (Figure 2). Qwen Untuned is the most action-heavy at approximately 94% active and 6% passive. OpenAI is similar at roughly 89% active and 10% passive. Qwen Fine-Tuned, by contrast, allocates approximately 82% of turns to active strategies and 18% to passive ones — nearly double the passive share of OpenAI and triple that of Qwen Untuned. In a supportive dialogue context, passive strategies correspond to listening-oriented moves (asking questions, reflecting back what was said), while active strategies correspond to action-oriented moves (giving advice, offering plans, affirming). The fine-tuned model's higher passive share suggests it spends more of the conversation in a listening posture before moving to advice, which aligns with the training objective of encouraging clarification and understanding before action.

**Diversity score.** The composite diversity score, which combines entropy, unique-strategy count, same-strategy rate, and the share of fully monotonic conversations, is 5.720 for Qwen Fine-Tuned, compared with 5.129 for OpenAI and 5.036 for Qwen Untuned (Figure 5). This represents a 12% improvement over OpenAI and a 14% improvement over Qwen Untuned. It is worth noting that entropy alone does not distinguish between meaningful, context-appropriate variation and random switching. The question of whether this diversity is genuinely adaptive is addressed further in the Discussion.

#### Context-sensitive sequencing (Feature 2)

The metrics above directly address Feature 1: whether the fine-tuned model avoids monotonous response patterns by varying its conversational strategies. Feature 2 — whether those strategy shifts are context-sensitive rather than random — was not explicitly measured by our evaluation framework. Our metrics capture *that* the model switches strategies, but not *whether it switches at the right time*. Nonetheless, several patterns in the data are at least consistent with context-sensitive behaviour, even if they do not constitute direct evidence.

The clearest signal is the concentration of probing at turn 1. The training data required the first assistant response to probe or clarify before advising, reflecting the intuition that when a caregiver's situation has just been introduced, the appropriate first move is to understand rather than to act. Qwen Fine-Tuned probes at 33% on turn 1 — roughly 5 times the rate of OpenAI (6%) and 1.5 times that of Qwen Untuned (21%). If the fine-tuned model were distributing probes randomly for the sake of variety, we would expect a roughly uniform probing rate across all turns. Instead, the rate is highest precisely where context is thinnest. This does not prove that the model is reasoning about uncertainty, but the pattern is consistent with a learned heuristic that favours clarification early in a conversation.

More broadly, the turn-by-turn data reveals a macro arc across all three models: early turns are dominated by understanding-oriented strategies (`validate`, `reflect`, `probe`), while later turns shift toward action-oriented strategies (`suggest`, `support`, `plan`). This arc is not unique to the fine-tuned model — it appears in the baselines as well — which suggests it reflects a general property of how supportive conversations tend to unfold. What distinguishes Qwen Fine-Tuned is that this transition is more gradual. The fine-tuned model retains higher rates of `probe` (5–8%) and `reflect` (3–5%) through turns 6–10, whereas OpenAI and Qwen Untuned become almost entirely dominated by active strategies by mid-conversation. This more gradual shift could indicate that the model is continuing to gather context even in later turns rather than assuming it has enough information to advise, though it could equally reflect a general bias toward exploratory moves introduced by the training distribution.

Our current framework cannot distinguish between these two explanations. Confirming context-sensitivity would require either human annotation of whether individual strategy switches align with changes in the preceding user turn, or a conditional metric that evaluates whether the choice of strategy at each position is appropriate given the conversational state at that point. We note this as an important gap and a direction for future evaluation work.

#### Generalisation to longer contexts (3-turn vs 10-turn)

One observation that warrants separate attention is the relationship between training length and evaluation length. The fine-tuning dataset consisted exclusively of 3-turn conversations (3 user turns and 3 assistant turns). Yet the evaluation uses 10-turn conversations, more than three times the training length.

If the model had merely memorised the format of the training data, we would expect its behaviour to degrade or become repetitive after turn 3. Instead, the data shows that probing, strategy switching, and structural variation persist through turns 4–10. The model continues to use 5–8% probing at later turns and maintains a higher switch rate and lower same-strategy percentage than both baselines throughout the full 10-turn dialogue.

This suggests that fine-tuning shifted the model's general response tendencies rather than teaching it a fixed 3-turn template. The model appears to have picked up on underlying conversational patterns — when to clarify, when to shift strategy, how to avoid repetition — and applies them beyond the training horizon. The implications of this observation are discussed further in the Discussion section.

#### Summary

Taken together, these results are encouraging given the constraints of the project. The fine-tuning dataset was generated rather than human-authored, the training conversations were only 3 turns long, the model is a 7-billion-parameter open-weight model rather than a frontier system, and the evaluation is based on 57–100 simulated conversations rather than large-scale human trials. Despite these limitations, the fine-tuned Qwen model outperforms both baselines on every diversity metric we measured: it uses more unique strategies per conversation, switches between them more often, repeats its dominant strategy less, achieves higher entropy, and scores 12–14% higher on the composite diversity measure. The fact that these improvements are consistent across per-conversation distributions (Figure 4) rather than driven by outliers, and that they persist beyond the training horizon into turns 4–10, suggests that even a modest, imperfect fine-tuning intervention can produce a meaningful shift in conversational behaviour. The remaining question — whether this increased diversity translates into genuinely better emotional support — is addressed in the Discussion.

## Discussion

Our work suggests that conversational diversity is not only a matter of varying content, but also of varying conversational structure. Responses that alternate between probing, reflection, acknowledgement, and guidance feel more natural than responses that follow the same template each time.

At the same time, our project also highlighted the difficulty of evaluating emotionally supportive dialogue. While quantitative metrics help us operationalise diversity in a consistent way, they remain proxies for broader qualities such as naturalness and emotional supportiveness. This means improvement on our metrics should be interpreted carefully rather than treated as direct proof of better emotional support.

### Generalisation beyond training length

The most encouraging result from the evaluation is the fine-tuned model's ability to sustain diverse behaviour across 10-turn conversations despite being trained exclusively on 3-turn examples. If fine-tuning had only taught the model a fixed 3-turn conversational template, we would expect its diversity advantages to collapse after turn 3, reverting to the base model's default patterns for the remaining turns. Instead, the turn-by-turn data shows that probing persists at 5–8% through turns 7–10, strategy switching remains elevated throughout, and the same-strategy rate stays lower than both baselines at every turn position.

This pattern suggests that fine-tuning altered the model's general conversational tendencies rather than imprinting a rigid format. In other words, the model appears to have learned something closer to "probe when the situation is unclear" and "avoid repeating the same strategy consecutively" than "at turn 1 probe, at turn 2 validate, at turn 3 suggest." The fact that these patterns transfer beyond the training horizon is a positive indicator of genuine pattern acquisition.

That said, we cannot fully isolate the contribution of fine-tuning from the base model's existing instruction-following ability. Qwen2.5-7B-Instruct already has a general capacity for multi-turn dialogue, and it is possible that some of the sustained diversity at later turns reflects the base model's ability to maintain coherent behaviour over longer contexts rather than a skill specifically introduced by fine-tuning. Disentangling these two contributions would require a more controlled experiment, for example fine-tuning on conversations of varying lengths and comparing the point at which each model's diversity degrades.

### Mechanical versus meaningful diversity

While the fine-tuned model outperforms both baselines on every diversity metric, the entropy gap is modest: 2.201 versus 2.163 for OpenAI, corresponding to 78.5% versus 77.1% of the theoretical maximum for 7 strategies. This raises the question of whether the observed improvement reflects genuinely more context-sensitive responses or simply more frequent switching between strategies without regard to conversational context.

Several pieces of evidence lean toward meaningful rather than mechanical diversity. First, the increase in probing is concentrated at turn 1, where it is most contextually appropriate: the user has just introduced a situation, and clarification is a natural first move. If the model were switching randomly, we would expect probing to be distributed uniformly across turns rather than front-loaded. Second, the validate spike at turn 2 — present in all three models — suggests that fine-tuning did not override sensible conversational reflexes. The model still acknowledges the user's first substantive message before moving on, just with a less extreme dominance of that single strategy. Third, the late-turn convergence toward suggest and support is consistent across all three systems and aligns with the intuitive expectation that later turns in a supportive conversation tend to shift toward actionable guidance.

However, we cannot confirm that the diversity is genuinely adaptive without human evaluation. It remains possible that some of the additional strategy switches are abrupt or poorly timed, producing conversations that score well on our metrics while feeling less coherent to a human reader. Future work should include qualitative review of individual conversations to assess whether increased switching corresponds to appropriate conversational transitions.

### Preliminary data

The results for Qwen Untuned are based on 57 of the planned 100 role-card scenarios, due to an incomplete batch run. While the patterns observed are directionally consistent and the metrics are stable enough to report, the final numbers for Qwen Untuned may shift once the remaining 43 conversations are processed. The OpenAI and Qwen Fine-Tuned runs are complete at 100 scenarios each. We flag this as a caveat throughout the results rather than deferring all reporting until the batch is finished, because the relative ordering of the three systems is unlikely to change given the consistency of the current data.

## Limitations

In hindsight, rather than constructing caregiver personas based on our own assumptions, we would have grounded them in real clinical use cases. Drawing from documented caregiver profiles or established research would have given our personas greater validity and ensured the system was evaluated against needs that are actually representative of the population it aims to serve. More fundamentally, we did not directly consult caregivers in designing either the personas or the criteria. This means that some of the conversational patterns we treated as desirable may reflect our own assumptions about good support more than the priorities of actual caregiver users.

More broadly, our work surfaced two limitations that extend beyond our specific implementation. The first is related to the nature of the subset we chose to optimise for. In prioritising compatibility across cases over diversity of cases, we narrowed the scope of what our system was trained to handle. Conversational diversity, as we defined it, may not be fully generalisable, as emotionally supportive dialogue varies across different caregiving contexts, and a metric designed for one subset may not transfer well to another.

The second is a more fundamental tension, and one discussed in class as well: when a measure becomes a target, it ceases to be a good measure. By directly optimising for conversational diversity, we risk a system that performs well on our metrics without genuinely improving emotional support. The metric was intended to serve as a proxy for quality, but optimising for it directly detaches it from the underlying quality it was meant to reflect. This is a failure mode in our evaluation design, and one we would approach more carefully in future work.

## Next Steps

Possible next steps include:

- grounding caregiver personas in real clinical use cases
- exploring personalisation beyond generic diversity
- testing whether diversity improvements generalise across different caregiving scenarios
- revisiting whether our current diversity metrics remain valid once optimisation explicitly targets them
- incorporating responsiveness to uncertainty, such as whether the model clarifies vague user inputs instead of responding with unwarranted confidence
- evaluating balance between understanding and action, rather than treating empathy and advice as interchangeable signs of good support
- evaluating local coherence, such as whether each turn responds appropriately to the immediately preceding context
- distinguishing meaningful variation from mechanical variation, so that strategy shifts are assessed for appropriateness rather than variety alone

# References

_Singapore Medical Council_. (2016). https://isomer-user-content.by.gov.sg/77/775548fb-11df-4393-89c5-33717769ccf6/2016-smc-ethical-code-and-ethical-guidelines---(13sep16).pdf

Ward, N., & Wataru Tsukahara. (2003). A study in responsiveness in spoken dialog. _International Journal of Human-Computer Studies_, _59_(5), 603-630. https://doi.org/10.1016/s1071-5819(03)00085-5

Zhao, H., Li, L., Chen, S., Kong, S., Wang, J., Huang, K., Gu, T., Wang, Y., Wang, J., Liang, D., Li, Z., Teng, Y., Xiao, Y., & Wang, Y. (2024). _ESC-Eval: Evaluating Emotion Support Conversations in Large Language Models_ (p. 15785). https://aclanthology.org/2024.emnlp-main.883.pdf

Lin, X., Yu, X., Aich, A., Giorgi, S., & Ungar, L. (2024). _DiverseDialogue: A methodology for designing chatbots with human-like diversity_. arXiv. https://arxiv.org/abs/2409.00262

Heyn, L., Torp Lokkeberg, S., Ellington, L., van Dulmen, S., & Eide, H. (2023). _Understanding the role of positive emotions in healthcare communication - A realist review_. Nursing Open, 10.
