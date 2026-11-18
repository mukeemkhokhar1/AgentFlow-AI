from typing import Any
import re

class PlannerAgent:
    """Turns a natural-language request into a small, transparent task plan."""
    def plan(self, request: str) -> list[str]:
        text = request.strip()
        if len(text) < 5:
            raise ValueError("Please enter a more detailed task (at least 5 characters).")
        # Keep the MVP deterministic and auditable rather than pretending to use an LLM.
        lower = text.lower()
        if any(word in lower for word in ("report", "summary", "analyse", "analyze")):
            return [
                "Clarify the requested outcome and identify required information",
                "Organize the available information into key findings",
                "Prepare a structured report with actions and open questions",
            ]
        if any(word in lower for word in ("email", "message", "customer", "reply")):
            return [
                "Identify the recipient, purpose and required tone",
                "Draft a clear response with the necessary details",
                "Review the draft for completeness and professionalism",
            ]
        if any(word in lower for word in ("project", "plan", "launch", "build")):
            return [
                "Define the desired outcome and constraints",
                "Break the work into ordered milestones",
                "Create a prioritized action checklist",
            ]
        return [
            "Understand the requested outcome and constraints",
            "Break the request into actionable steps",
            "Prepare the result and identify any follow-up actions",
        ]

class ExecutionAgent:
    """Executes safe planning steps as a tracked workflow simulation."""
    def execute(self, steps: list[str]) -> list[dict[str, Any]]:
        return [
            {"step": i + 1, "task": task, "status": "completed",
             "output": f"Completed: {task}"}
            for i, task in enumerate(steps)
        ]

class ReviewAgent:
    """Checks that the workflow has a plan and all steps completed."""
    def review(self, plan: list[str], results: list[dict[str, Any]]) -> dict[str, Any]:
        completed = sum(item["status"] == "completed" for item in results)
        passed = bool(plan) and completed == len(plan)
        return {
            "passed": passed,
            "completed_steps": completed,
            "total_steps": len(plan),
            "message": "All planned steps completed." if passed else "Review found incomplete steps.",
        }

def run_workflow(request: str) -> dict[str, Any]:
    planner = PlannerAgent()
    executor = ExecutionAgent()
    reviewer = ReviewAgent()
    plan = planner.plan(request)
    results = executor.execute(plan)
    review = reviewer.review(plan, results)
    return {
        "request": request.strip(),
        "status": "completed" if review["passed"] else "needs_review",
        "agents": ["Planner Agent", "Execution Agent", "Review Agent"],
        "plan": plan,
        "results": results,
        "review": review,
    }
