# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "pandas>=2.2",
#     "altair>=5.4",
#     "python-dotenv>=1.0",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    import math
    import sys
    from collections import Counter, defaultdict
    from html import escape
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd
    from dotenv import load_dotenv

    REPO_ROOT = Path(__file__).resolve().parents[1]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    load_dotenv(REPO_ROOT / ".env")
    return (
        Counter,
        Path,
        REPO_ROOT,
        alt,
        defaultdict,
        escape,
        json,
        math,
        mo,
        pd,
    )


@app.cell
def _(REPO_ROOT):
    FINAL_RUNS_ROOT = REPO_ROOT / "final_runs"
    return (FINAL_RUNS_ROOT,)


@app.cell(hide_code=True)
def _(Counter, FINAL_RUNS_ROOT, Path, defaultdict, escape, json, math, pd):
    def load_json(path):
        return json.loads(path.read_text(encoding="utf-8"))

    def analyze_run(run_dir):
        run_dir = Path(run_dir)
        tags_dir = run_dir / "tags"

        tag_payloads = [
            load_json(path) for path in sorted(tags_dir.glob("*.tags.json"))
        ]
        per_turn_rows = []
        conversation_rows = []

        overall_strategy_counts = Counter()
        structure_by_turn = defaultdict(Counter)
        strategy_by_turn = defaultdict(Counter)
        same_strategy_percentages = []
        total_friend_turns = 0

        for payload in tag_payloads:
            strategies = []
            structures = []
            per_conversation_strategy_counts = Counter()

            for tag in payload["friend_turn_tags"]:
                per_turn_rows.append(
                    {
                        "run_id": payload["run_id"],
                        "conversation_id": payload["conversation_id"],
                        "role_card_id": payload["role_card_id"],
                        "friend_turn_index": tag["friend_turn_index"],
                        "message_position_1_based": tag["message_position_1_based"],
                        "structure": tag["structure"],
                        "primary_strategy": tag["primary_strategy"],
                        "secondary_strategies": "|".join(tag["secondary_strategies"]),
                        "confidence": tag.get("confidence", ""),
                        "tagger_version": payload["tagger"]["tagger_version"],
                        "taxonomy_version": payload["tagger"]["taxonomy_version"],
                    }
                )

                strategies.append(tag["primary_strategy"])
                structures.append(tag["structure"])
                per_conversation_strategy_counts[tag["primary_strategy"]] += 1
                overall_strategy_counts[tag["primary_strategy"]] += 1
                structure_by_turn[tag["friend_turn_index"]][tag["structure"]] += 1
                strategy_by_turn[tag["friend_turn_index"]][tag["primary_strategy"]] += 1
                total_friend_turns += 1

            dominant_strategy = ""
            dominant_share = 0.0
            same_primary_strategy_percentage = 0.0
            if per_conversation_strategy_counts:
                dominant_strategy, dominant_count = (
                    per_conversation_strategy_counts.most_common(1)[0]
                )
                dominant_share = dominant_count / len(strategies)
                same_primary_strategy_percentage = dominant_share * 100
                same_strategy_percentages.append(same_primary_strategy_percentage)

            conversation_rows.append(
                {
                    "run_id": payload["run_id"],
                    "conversation_id": payload["conversation_id"],
                    "role_card_id": payload["role_card_id"],
                    "friend_turn_count": len(strategies),
                    "unique_primary_strategies": len(set(strategies)),
                    "dominant_primary_strategy": dominant_strategy,
                    "dominant_primary_strategy_share": round(dominant_share, 4),
                    "same_primary_strategy_percentage": round(
                        same_primary_strategy_percentage, 2
                    ),
                    "all_same_primary_strategy": len(set(strategies)) == 1,
                    "strategy_sequence": "|".join(strategies),
                    "structure_sequence": "|".join(structures),
                }
            )

        overall_strategy_share = []
        for strategy, count in sorted(overall_strategy_counts.items()):
            overall_strategy_share.append(
                {
                    "primary_strategy": strategy,
                    "count": count,
                    "share": round(count / total_friend_turns, 4)
                    if total_friend_turns
                    else 0.0,
                    "percentage": round((count / total_friend_turns) * 100, 2)
                    if total_friend_turns
                    else 0.0,
                }
            )

        turn_position_structure_share = []
        for turn_index in sorted(structure_by_turn):
            turn_total = sum(structure_by_turn[turn_index].values())
            for structure, count in sorted(structure_by_turn[turn_index].items()):
                turn_position_structure_share.append(
                    {
                        "friend_turn_index": turn_index,
                        "structure": structure,
                        "count": count,
                        "share": round(count / turn_total, 4) if turn_total else 0.0,
                        "percentage": round((count / turn_total) * 100, 2)
                        if turn_total
                        else 0.0,
                    }
                )

        turn_position_strategy_share = []
        for turn_index in sorted(strategy_by_turn):
            turn_total = sum(strategy_by_turn[turn_index].values())
            for strategy, count in sorted(strategy_by_turn[turn_index].items()):
                turn_position_strategy_share.append(
                    {
                        "friend_turn_index": turn_index,
                        "primary_strategy": strategy,
                        "count": count,
                        "share": round(count / turn_total, 4) if turn_total else 0.0,
                        "percentage": round((count / turn_total) * 100, 2)
                        if turn_total
                        else 0.0,
                    }
                )

        run_summary = {
            "run_id": run_dir.name,
            "conversation_count": len(conversation_rows),
            "friend_turn_count": total_friend_turns,
            "average_same_primary_strategy_percentage": round(
                sum(same_strategy_percentages) / len(same_strategy_percentages), 2
            )
            if same_strategy_percentages
            else 0.0,
            "overall_strategy_share": overall_strategy_share,
            "turn_position_structure_share": turn_position_structure_share,
            "turn_position_strategy_share": turn_position_strategy_share,
        }

        return {
            "summary": run_summary,
            "conversation_rows": conversation_rows,
            "per_turn_rows": per_turn_rows,
        }

    def load_run_config(run_dir):
        path = run_dir / "config" / "run-config.json"
        return load_json(path) if path.is_file() else {"run_id": run_dir.name}

    def list_run_dirs():
        if not FINAL_RUNS_ROOT.is_dir():
            return []
        run_dirs = []
        for path in FINAL_RUNS_ROOT.iterdir():
            if path.is_dir() and (path / "conversations").is_dir():
                run_dirs.append(path)
        return sorted(run_dirs, key=lambda item: item.stat().st_mtime, reverse=True)

    def build_run_label(run_dir):
        config = load_run_config(run_dir)
        friend_agent = config.get("friend_agent", "unknown_friend")
        tagger = config.get("tagger", "unknown_tagger")
        return f"{run_dir.name} | {friend_agent} | {tagger}"

    def clip_text(text, limit=220):
        compact = " ".join(str(text).split())
        return (
            compact if len(compact) <= limit else compact[: limit - 3].rstrip() + "..."
        )

    def strategy_switch_count(sequence):
        items = [item for item in str(sequence).split("|") if item]
        return sum(left != right for left, right in zip(items, items[1:]))

    def entropy_from_counts(counts):
        total = sum(counts)
        if not total:
            return 0.0
        value = 0.0
        for count in counts:
            share = count / total
            value -= share * math.log2(share)
        return round(value, 3)

    def friendly_run_name(run_id):
        if "qwen_base" in run_id:
            return "Qwen Untuned"
        if "qwen" in run_id:
            return "Qwen Fine-Tuned"
        if "openai" in run_id:
            return "OpenAI"
        return run_id

    ACTIVE_STRATEGIES = {"plan", "suggest", "support", "validate"}
    PASSIVE_STRATEGIES = {"probe", "reflect"}

    def group_strategy(strategy):
        lower = strategy.lower()
        if lower in ACTIVE_STRATEGIES:
            return "Active"
        if lower in PASSIVE_STRATEGIES:
            return "Passive"
        return "Other"

    RUN_DISPLAY_ORDER = {"OpenAI": 0, "Qwen Fine-Tuned": 1, "Qwen Untuned": 2}

    def load_role_cards(run_dir):
        snapshot_path = run_dir / "role-cards" / "role_cards.snapshot.json"
        if not snapshot_path.is_file():
            return {}
        return {row["role_card_id"]: row for row in load_json(snapshot_path)}

    def load_conversations(run_dir):
        conversations = {}
        for path in sorted((run_dir / "conversations").glob("*.json")):
            conversations[path.stem] = load_json(path)
        return conversations

    def load_tags(run_dir):
        tags = {}
        for path in sorted((run_dir / "tags").glob("*.tags.json")):
            tags[path.name.replace(".tags.json", "")] = load_json(path)
        return tags

    def enrich_conversation_metrics(conversation_df, turn_df):
        if conversation_df.empty:
            return conversation_df

        result = conversation_df.copy()
        result["switch_count"] = result["strategy_sequence"].apply(
            strategy_switch_count
        )
        result["normalized_unique_strategy_share"] = (
            result["unique_primary_strategies"] / result["friend_turn_count"]
        ).round(3)

        if turn_df.empty:
            result["average_confidence"] = 0.0
            result["secondary_strategy_variety"] = 0
            return result

        confidence_df = (
            turn_df.groupby("conversation_id", as_index=False)["confidence"]
            .mean()
            .rename(columns={"confidence": "average_confidence"})
            .round({"average_confidence": 3})
        )

        secondary_rows = []
        for row in turn_df[["conversation_id", "secondary_strategies"]].to_dict(
            "records"
        ):
            secondary = [
                item for item in str(row["secondary_strategies"]).split("|") if item
            ]
            secondary_rows.append(
                {
                    "conversation_id": row["conversation_id"],
                    "secondary_strategy_variety": len(set(secondary)),
                }
            )

        secondary_df = (
            pd.DataFrame(secondary_rows)
            .groupby("conversation_id", as_index=False)["secondary_strategy_variety"]
            .sum()
        )

        return (
            result.merge(confidence_df, on="conversation_id", how="left")
            .merge(secondary_df, on="conversation_id", how="left")
            .fillna({"average_confidence": 0.0, "secondary_strategy_variety": 0})
        )

    def first_quote(conversation, speaker):
        for message in conversation.get("messages", []):
            if message.get("speaker") == speaker:
                return clip_text(message.get("text", ""))
        return ""

    def build_qualitative_insights(conversation_df, conversations, role_cards):
        if conversation_df.empty:
            return {}

        diverse = conversation_df.sort_values(
            [
                "unique_primary_strategies",
                "switch_count",
                "same_primary_strategy_percentage",
            ],
            ascending=[False, False, True],
        ).iloc[0]
        monotonic = conversation_df.sort_values(
            [
                "same_primary_strategy_percentage",
                "unique_primary_strategies",
                "switch_count",
            ],
            ascending=[False, True, True],
        ).iloc[0]
        switching = conversation_df.sort_values(
            ["switch_count", "unique_primary_strategies", "average_confidence"],
            ascending=[False, False, False],
        ).iloc[0]

        def pack(row):
            conversation = conversations[row["conversation_id"]]
            role_card = role_cards.get(row["role_card_id"], {})
            scenario = role_card.get("scenario", {})
            return {
                "conversation_id": row["conversation_id"],
                "role_card_id": row["role_card_id"],
                "scenario_type": scenario.get("type", "unknown"),
                "unique_primary_strategies": int(row["unique_primary_strategies"]),
                "same_primary_strategy_percentage": float(
                    row["same_primary_strategy_percentage"]
                ),
                "switch_count": int(row["switch_count"]),
                "opening_quote": first_quote(conversation, "victim"),
                "friend_quote": first_quote(conversation, "friend"),
            }

        return {
            "most_diverse": pack(diverse),
            "most_monotonic": pack(monotonic),
            "most_switching": pack(switching),
        }

    def ensure_run_outputs(run_dir):
        config = load_run_config(run_dir)
        conversations = load_conversations(run_dir)
        tags = load_tags(run_dir)
        missing_tag_ids = sorted(set(conversations) - set(tags))
        if missing_tag_ids:
            raise FileNotFoundError(
                f"Missing tag files for run {run_dir.name}: {', '.join(missing_tag_ids)}"
            )

        analysis = analyze_run(run_dir)
        summary = analysis["summary"]
        role_cards = load_role_cards(run_dir)
        conversation_df = pd.DataFrame(analysis["conversation_rows"])
        turn_df = pd.DataFrame(analysis["per_turn_rows"])
        conversation_df = enrich_conversation_metrics(conversation_df, turn_df)
        overall_strategy_df = pd.DataFrame(summary.get("overall_strategy_share", []))
        turn_strategy_df = pd.DataFrame(summary.get("turn_position_strategy_share", []))

        mean_unique = (
            round(float(conversation_df["unique_primary_strategies"].mean()), 3)
            if not conversation_df.empty
            else 0.0
        )
        share_all_same = (
            round(float(conversation_df["all_same_primary_strategy"].mean()), 3)
            if not conversation_df.empty
            else 0.0
        )
        mean_switch = (
            round(float(conversation_df["switch_count"].mean()), 3)
            if not conversation_df.empty
            else 0.0
        )
        strategy_entropy = (
            entropy_from_counts(overall_strategy_df["count"].tolist())
            if not overall_strategy_df.empty
            else 0.0
        )

        comparison_metrics = {
            "run_id": run_dir.name,
            "friend_agent": config.get("friend_agent", "unknown_friend"),
            "tagger": config.get("tagger", "unknown_tagger"),
            "conversation_count": int(summary.get("conversation_count", 0)),
            "friend_turn_count": int(summary.get("friend_turn_count", 0)),
            "average_same_primary_strategy_percentage": float(
                summary.get("average_same_primary_strategy_percentage", 0.0)
            ),
            "mean_unique_primary_strategies": mean_unique,
            "share_all_same_primary_strategy": share_all_same,
            "mean_switch_count": mean_switch,
            "strategy_entropy": strategy_entropy,
        }
        comparison_metrics["diversity_score"] = round(
            comparison_metrics["strategy_entropy"]
            + comparison_metrics["mean_unique_primary_strategies"]
            - (comparison_metrics["average_same_primary_strategy_percentage"] / 100.0)
            - comparison_metrics["share_all_same_primary_strategy"],
            3,
        )

        qualitative_insights = build_qualitative_insights(
            conversation_df, conversations, role_cards
        )

        return {
            "run_dir": run_dir,
            "config": config,
            "summary": summary,
            "conversations": conversations,
            "tags": tags,
            "role_cards": role_cards,
            "conversation_df": conversation_df,
            "turn_df": turn_df,
            "overall_strategy_df": overall_strategy_df,
            "turn_strategy_df": turn_strategy_df,
            "comparison_metrics": comparison_metrics,
            "qualitative_insights": qualitative_insights,
        }

    def render_role_card(role_card):
        if not role_card:
            return "<div>No role card available.</div>"
        blocks = []
        for title, payload in [
            ("Persona", role_card.get("persona", {})),
            ("Care details", role_card.get("care_details", {})),
            ("Scenario", role_card.get("scenario", {})),
            ("Vulnerability style", role_card.get("vulnerability_style", {})),
            ("Conversation seed", role_card.get("conversation_seed", {})),
        ]:
            items = "".join(
                f"<li><strong>{escape(str(key))}</strong>: {escape(str(value))}</li>"
                for key, value in payload.items()
            )
            blocks.append(
                "<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px'>"
                f"<h4 style='margin:0 0 8px 0'>{escape(title)}</h4><ul style='margin:0;padding-left:18px'>{items}</ul></div>"
            )
        return (
            f"<div><div style='font-size:20px;font-weight:700;margin-bottom:12px'>Role card: {escape(role_card.get('role_card_id', 'unknown'))}</div>"
            + "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px'>"
            + "".join(blocks)
            + "</div></div>"
        )

    def render_conversation(conversation, tag_payload):
        tag_map = {
            tag["friend_turn_index"]: tag
            for tag in tag_payload.get("friend_turn_tags", [])
        }
        pieces = []
        for message in conversation.get("messages", []):
            is_friend = message.get("speaker") == "friend"
            tag = tag_map.get(message.get("turn_index"), {}) if is_friend else {}
            annotation = ""
            if tag:
                secondary = ", ".join(tag.get("secondary_strategies", [])) or "none"
                annotation = (
                    "<div style='margin-top:8px;font-size:12px;color:#166534'>"
                    f"structure: {escape(str(tag.get('structure', '')))} | primary: {escape(str(tag.get('primary_strategy', '')))} | secondary: {escape(secondary)} | confidence: {escape(str(tag.get('confidence', '')))}"
                    "</div>"
                    f"<div style='margin-top:6px;font-size:12px;color:#166534'>{escape(str(tag.get('notes', '')))}</div>"
                )
            pieces.append(
                "<div style='display:flex;justify-content:"
                + ("flex-end" if is_friend else "flex-start")
                + ";margin:12px 0'>"
                + "<div style='max-width:78%;border-radius:18px;padding:14px 16px;box-shadow:0 6px 18px rgba(15,23,42,.08);background:"
                + ("#dcfce7" if is_friend else "#eff6ff")
                + ";border:1px solid "
                + ("#86efac" if is_friend else "#bfdbfe")
                + "'>"
                + f"<div style='font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#475569;margin-bottom:8px'>{escape(message.get('speaker', 'unknown'))} · turn {escape(str(message.get('turn_index', '')))}</div>"
                + f"<div style='font-size:14px;line-height:1.55;white-space:pre-wrap'>{escape(str(message.get('text', '')))}</div>"
                + annotation
                + "</div></div>"
            )
        return "<div>" + "".join(pieces) + "</div>"

    def research_readout(comparison_df):
        if comparison_df.empty:
            return "No runs selected."
        if len(comparison_df) == 1:
            row = comparison_df.iloc[0]
            name = friendly_run_name(row["run_id"])
            return f"Only one run is selected. **{name}** has entropy {row['strategy_entropy']:.3f}, mean unique strategies {row['mean_unique_primary_strategies']:.2f}, and repeated-strategy rate {row['average_same_primary_strategy_percentage']:.2f}%."
        ranked = comparison_df.sort_values(
            [
                "diversity_score",
                "strategy_entropy",
                "mean_unique_primary_strategies",
                "average_same_primary_strategy_percentage",
            ],
            ascending=[False, False, False, True],
        )
        best = ranked.iloc[0]
        worst = ranked.iloc[-1]
        best_name = friendly_run_name(best["run_id"])
        worst_name = friendly_run_name(worst["run_id"])
        return f"Higher entropy and unique-strategy counts, together with lower repeated-strategy rate, indicate more diverse responses. Among the selected runs, **{best_name}** currently looks strongest on diversity (score {best['diversity_score']:.3f}), while **{worst_name}** looks most repetitive (score {worst['diversity_score']:.3f})."

    return (
        RUN_DISPLAY_ORDER,
        build_run_label,
        ensure_run_outputs,
        friendly_run_name,
        group_strategy,
        list_run_dirs,
        render_conversation,
        render_role_card,
        research_readout,
    )


@app.cell
def _(build_run_label, list_run_dirs):
    run_dirs = list_run_dirs()
    run_options = {build_run_label(run_dir): run_dir.name for run_dir in run_dirs}
    if not run_options:
        run_options = {"No runs found under final_runs/": ""}
    default_run_id = run_dirs[0].name if run_dirs else ""
    return default_run_id, run_dirs, run_options


@app.cell
def _(RUN_DISPLAY_ORDER, ensure_run_outputs, friendly_run_name, run_dirs):
    all_bundles = sorted(
        [ensure_run_outputs(rd) for rd in run_dirs],
        key=lambda b: RUN_DISPLAY_ORDER.get(friendly_run_name(b["run_dir"].name), 99),
    )
    return (all_bundles,)


@app.cell
def _(default_run_id, mo, run_options):
    dropdown_options = {run_id: label for label, run_id in run_options.items()}
    run_selector = mo.ui.dropdown(
        options=dropdown_options, value=default_run_id, label="Primary run"
    )
    controls = mo.vstack(
        [
            mo.md("## Run Selection"),
            mo.md(
                "The notebook expects exactly three runs under `final_runs/<run_id>/` with fully populated `tags/`. It compares those three runs automatically and uses this dropdown only for the detailed single-run view."
            ),
            run_selector,
        ]
    )
    controls
    return (run_selector,)


@app.cell
def _(all_bundles, run_selector):
    selected_run_id = run_selector.value
    if selected_run_id and " | " in selected_run_id:
        selected_run_id = selected_run_id.split(" | ")[0]
    primary_bundle = next(
        (bundle for bundle in all_bundles if bundle["run_dir"].name == selected_run_id),
        all_bundles[0] if all_bundles else None,
    )
    return (primary_bundle,)


@app.cell
def _(FINAL_RUNS_ROOT, mo, primary_bundle):
    ls_output = (
        "\n".join(sorted(path.name for path in FINAL_RUNS_ROOT.iterdir()))
        if FINAL_RUNS_ROOT.is_dir()
        else "<missing>"
    )
    header = (
        mo.md(
            "# Final Run Review\n"
            "```\n"
            f"$ ls final_runs\n{ls_output}\n"
            "```\n"
            "No runs found under `final_runs/` yet. Add a workspace at `final_runs/<run_id>/`."
        )
        if primary_bundle is None
        else mo.vstack(
            [
                mo.md(f"# Final Run Review: `{primary_bundle['run_dir'].name}`"),
                mo.md(
                    f"Friend agent: `{primary_bundle['comparison_metrics']['friend_agent']}`\n"
                    f"Tagger: `{primary_bundle['comparison_metrics']['tagger']}`"
                ),
            ]
        )
    )
    header
    return


@app.cell
def _(mo, primary_bundle):
    body = (
        mo.md("## Processing Status\nNo primary run selected.")
        if primary_bundle is None
        else mo.md(
            "## Processing Status\n"
            f"- Conversations found: `{len(primary_bundle['conversations'])}`\n"
            f"- Tagged conversations loaded: `{len(primary_bundle['tags'])}`"
        )
    )
    body
    return


@app.cell
def _(all_bundles, alt, friendly_run_name, group_strategy, mo, pd):
    _frames = []
    for _bundle in all_bundles:
        _name = friendly_run_name(_bundle["run_dir"].name)
        _df = _bundle["overall_strategy_df"].copy()
        if _df.empty:
            continue
        _df["run"] = _name
        _frames.append(_df)
    if _frames:
        _combined = pd.concat(_frames, ignore_index=True)
        _all_strategies = sorted(_combined["primary_strategy"].unique())
        _all_runs = [friendly_run_name(b["run_dir"].name) for b in all_bundles]
        _grid = pd.DataFrame(
            [(s, r) for s in _all_strategies for r in _all_runs],
            columns=["primary_strategy", "run"],
        )
        _combined = _grid.merge(
            _combined, on=["primary_strategy", "run"], how="left"
        ).fillna({"count": 0, "percentage": 0.0})
        _individual_chart = (
            alt.Chart(_combined)
            .mark_bar()
            .encode(
                x=alt.X("primary_strategy:N", title="Strategy"),
                xOffset=alt.XOffset("run:N"),
                y=alt.Y("percentage:Q", title="Share (%)"),
                color=alt.Color("run:N", title="Run"),
                tooltip=["run", "primary_strategy", "count", "percentage"],
            )
            .properties(title="Overall strategy distribution", height=340)
        )
        _gcombined = _combined.copy()
        _gcombined["group"] = _gcombined["primary_strategy"].apply(group_strategy)
        _gagg = _gcombined.groupby(["group", "run"], as_index=False).agg(
            count=("count", "sum"), percentage=("percentage", "sum")
        )
        _grouped_chart = (
            alt.Chart(_gagg)
            .mark_bar()
            .encode(
                x=alt.X("group:N", title="Strategy group"),
                xOffset=alt.XOffset("run:N"),
                y=alt.Y("percentage:Q", title="Share (%)"),
                color=alt.Color("run:N", title="Run"),
                tooltip=["run", "group", "count", "percentage"],
            )
            .properties(
                title="Grouped strategy distribution (Active vs Passive)",
                height=340,
            )
        )
        overall = mo.vstack(
            [
                mo.md("## Strategy Mix"),
                mo.md("### Individual Strategies"),
                _individual_chart,
                mo.md("### Grouped Strategies (Active vs Passive)"),
                _grouped_chart,
            ]
        )
    else:
        overall = mo.md("## Strategy Mix\nNo runs available.")
    overall
    return


@app.cell
def _(all_bundles, alt, friendly_run_name, mo, pd):
    _frames = []
    for _bundle in all_bundles:
        _name = friendly_run_name(_bundle["run_dir"].name)
        _df = _bundle["turn_strategy_df"].copy()
        if _df.empty:
            continue
        _df["run"] = _name
        _frames.append(_df)
    if _frames:
        _combined = pd.concat(_frames, ignore_index=True)
        _strategies = sorted(_combined["primary_strategy"].unique())
        _charts = []
        for _strat in _strategies:
            _sdf = _combined[_combined["primary_strategy"] == _strat]
            _charts.append(
                alt.Chart(_sdf)
                .mark_line(point=True, strokeWidth=3)
                .encode(
                    x=alt.X("friend_turn_index:O", title="Turn index"),
                    y=alt.Y("percentage:Q", title="Share (%)"),
                    color=alt.Color("run:N", title="Run"),
                    tooltip=["run", "friend_turn_index", "percentage", "count"],
                )
                .properties(title=_strat.capitalize(), width=280, height=240)
            )
        _row_size = 3
        _rows = [
            alt.hconcat(*_charts[i : i + _row_size])
            .resolve_scale(color="independent")
            .resolve_legend(color="independent")
            for i in range(0, len(_charts), _row_size)
        ]
        by_turn = mo.vstack(
            [mo.md("## Turn Dynamics")]
            + [alt.vconcat(*_rows).resolve_scale(color="independent")]
        )
    else:
        by_turn = mo.md("## Turn Dynamics\nNo runs available.")
    by_turn
    return


@app.cell
def _(all_bundles, alt, friendly_run_name, mo, pd):
    _frames = []
    for _bundle in all_bundles:
        _name = friendly_run_name(_bundle["run_dir"].name)
        _df = _bundle["conversation_df"].copy()
        if _df.empty:
            continue
        _df["run"] = _name
        _frames.append(_df)
    if _frames:
        _combined = pd.concat(_frames, ignore_index=True)
        _metrics = [
            ("unique_primary_strategies", "Unique strategies per conversation"),
            ("switch_count", "Strategy switches per conversation"),
            ("same_primary_strategy_percentage", "Same-strategy % per conversation"),
        ]
        _charts = []
        for _col, _title in _metrics:
            _charts.append(
                alt.Chart(_combined)
                .mark_boxplot(extent="min-max", size=40)
                .encode(
                    x=alt.X("run:N", title="Run"),
                    y=alt.Y(f"{_col}:Q", title=_title),
                    color=alt.Color("run:N", title="Run"),
                )
                .properties(title=_title, width=280, height=280)
            )
        distributions = mo.vstack(
            [
                mo.md("## Per-Conversation Metric Distributions"),
                alt.hconcat(*_charts).resolve_scale(color="independent"),
            ]
        )
    else:
        distributions = mo.md(
            "## Per-Conversation Metric Distributions\nNo runs available."
        )
    distributions
    return


@app.cell
def _(mo, primary_bundle):
    if primary_bundle is None:
        qualitative = mo.md("## Qualitative Highlights\nNo primary run selected.")
    else:
        sections = []
        for title, key in [
            ("Most diverse conversation", "most_diverse"),
            ("Most monotonic conversation", "most_monotonic"),
            ("Most switching conversation", "most_switching"),
        ]:
            insight = primary_bundle["qualitative_insights"].get(key, {})
            if insight:
                sections.append(
                    f"### {title}\n"
                    f"- Conversation: `{insight['conversation_id']}`\n"
                    f"- Role card: `{insight['role_card_id']}`\n"
                    f"- Scenario: `{insight['scenario_type']}`\n"
                    f"- Same primary strategy: `{insight['same_primary_strategy_percentage']:.2f}%`\n"
                    f"- Unique primary strategies: `{insight['unique_primary_strategies']}`\n"
                    f"- Strategy switches: `{insight['switch_count']}`\n"
                    f'- Victim opening quote: "{insight["opening_quote"]}"\n'
                    f'- Friend quote: "{insight["friend_quote"]}"'
                )
        qualitative = mo.md("## Qualitative Highlights\n\n" + "\n\n".join(sections))
    qualitative
    return


@app.cell
def _(mo, primary_bundle):
    if primary_bundle is None:
        conversation_options = {"No conversations available": ""}
        default_conversation = ""
    else:
        conversation_options = sorted(primary_bundle["conversations"].keys())
        default_conversation = conversation_options[0]
    conversation_selector = mo.ui.dropdown(
        options=conversation_options,
        value=default_conversation,
        label="Conversation to inspect",
    )
    conversation_selector
    return (conversation_selector,)


@app.cell
def _(conversation_selector, pd, primary_bundle):
    if primary_bundle is None or not conversation_selector.value:
        selected_conversation = {}
        selected_tag_payload = {}
        selected_role_card = {}
        selected_metrics_df = pd.DataFrame()
    else:
        selected_conversation = primary_bundle["conversations"][
            conversation_selector.value
        ]
        selected_tag_payload = primary_bundle["tags"][conversation_selector.value]
        selected_role_card = primary_bundle["role_cards"].get(
            selected_conversation["role_card_id"], {}
        )
        selected_metrics_df = primary_bundle["conversation_df"].loc[
            primary_bundle["conversation_df"]["conversation_id"]
            == conversation_selector.value
        ]
    return (
        selected_conversation,
        selected_metrics_df,
        selected_role_card,
        selected_tag_payload,
    )


@app.cell
def _(mo, selected_metrics_df):
    metrics_view = (
        mo.md("## Selected Conversation Metrics\nNo conversation selected.")
        if selected_metrics_df.empty
        else mo.vstack(
            [
                mo.md("## Selected Conversation Metrics"),
                mo.ui.table(selected_metrics_df.reset_index(drop=True)),
            ]
        )
    )
    metrics_view
    return


@app.cell
def _(mo, render_role_card, selected_role_card):
    role_card_view = (
        mo.md("## Role Card\nNo conversation selected.")
        if not selected_role_card
        else mo.vstack(
            [mo.md("## Role Card"), mo.Html(render_role_card(selected_role_card))]
        )
    )
    role_card_view
    return


@app.cell
def _(mo, render_conversation, selected_conversation, selected_tag_payload):
    conversation_view = (
        mo.md("## Conversation Viewer\nNo conversation selected.")
        if not selected_conversation
        else mo.vstack(
            [
                mo.md("## Conversation Viewer"),
                mo.Html(
                    render_conversation(selected_conversation, selected_tag_payload)
                ),
            ]
        )
    )
    conversation_view
    return


@app.cell
def _(all_bundles, pd):
    comparison_df = (
        pd.DataFrame()
        if not all_bundles
        else pd.DataFrame(
            [bundle["comparison_metrics"] for bundle in all_bundles]
        ).sort_values(
            [
                "diversity_score",
                "strategy_entropy",
                "mean_unique_primary_strategies",
                "average_same_primary_strategy_percentage",
            ],
            ascending=[False, False, False, True],
        )
    )
    return (comparison_df,)


@app.cell(hide_code=True)
def _(mo):
    formulae = mo.md(
        r"""
    ## How metrics are computed

    ### Strategy entropy

    Shannon entropy over the overall strategy frequency distribution:

    $$H = -\sum_{i=1}^{k} p_i \, \log_2(p_i)$$

    where $p_i$ is the share of friend turns tagged with strategy $i$ across the entire run, and $k$ is the number of distinct strategies observed. Higher entropy means the model spreads its turns more evenly across strategies.

    ### Diversity score

    A composite metric that rewards variety and penalises repetition:

    $$D = H + \bar{U} - \frac{\overline{S\%}}{100} - R_{\text{all-same}}$$

    | Symbol | Meaning |
    |--------|---------|
    | $H$ | Strategy entropy (defined above) |
    | $\bar{U}$ | Mean unique primary strategies per conversation |
    | $\overline{S\%}$ | Average same-primary-strategy percentage across conversations (divided by 100 to normalise to 0–1) |
    | $R_{\text{all-same}}$ | Share of conversations where every friend turn used the same primary strategy |

    A higher diversity score indicates a model that varies its strategy both **across** conversations and **within** each conversation.
    """
    )
    formulae
    return


@app.cell
def _(alt, comparison_df, friendly_run_name, mo):
    if comparison_df.empty:
        comparison_chart = mo.md(
            "## Cross-Run Comparison\nNo runs selected for comparison."
        )
    else:
        _plot_df = comparison_df.copy()
        _plot_df["display_name"] = _plot_df["run_id"].apply(friendly_run_name)
        comparison_chart = (
            alt.Chart(_plot_df)
            .mark_bar()
            .encode(
                x=alt.X("diversity_score:Q", title="Diversity score"),
                y=alt.Y("display_name:N", title="Run", sort=None),
                color=alt.Color("display_name:N", title="Run"),
                tooltip=[
                    "display_name",
                    "strategy_entropy",
                    "mean_unique_primary_strategies",
                    "average_same_primary_strategy_percentage",
                    "share_all_same_primary_strategy",
                    "diversity_score",
                ],
            )
            .properties(title="Cross-run diversity comparison", height=320)
        )
    comparison_chart
    return


@app.cell
def _(comparison_df, mo, research_readout):
    research = mo.md(
        "## Research Readout\n"
        + research_readout(comparison_df)
        + "\n\nUse this table to compare baseline and fine-tuned runs side by side."
    )
    research
    return


@app.cell
def _(comparison_df, friendly_run_name, mo):
    if comparison_df.empty:
        comparison_table = mo.md(
            "## Run Comparison Table\nNo runs selected for comparison."
        )
    else:
        _display_df = comparison_df.copy()
        _display_df.insert(
            0, "display_name", _display_df["run_id"].apply(friendly_run_name)
        )
        comparison_table = mo.vstack(
            [
                mo.md("## Run Comparison Table"),
                mo.ui.table(_display_df.reset_index(drop=True)),
            ]
        )
    comparison_table
    return


if __name__ == "__main__":
    app.run()
