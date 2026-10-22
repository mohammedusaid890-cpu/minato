(function () {
  "use strict";

  const form = document.getElementById("plan-form");
  const generateBtn = document.getElementById("generate-btn");
  const formError = document.getElementById("form-error");
  const resultsSection = document.getElementById("results");
  const replanBtn = document.getElementById("replan-btn");
  const printBtn = document.getElementById("print-btn");

  const rupee = (n) => "\u20B9" + Number(n).toLocaleString("en-IN");

  function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    generateBtn.classList.toggle("is-loading", isLoading);
  }

  function showError(message) {
    formError.textContent = message;
  }

  function clearError() {
    formError.textContent = "";
  }

  function animateBar(el, pct) {
    requestAnimationFrame(() => {
      el.style.width = Math.min(100, Math.max(4, pct)) + "%";
    });
  }

  function renderResults(data) {
    document.getElementById("result-eyebrow").textContent =
      `${data.days}-day ${data.style} trip`;
    document.getElementById("result-title").textContent = `Your ${data.destination} plan`;
    document.getElementById("model-note").textContent =
      `Cost model R\u00B2 ${data.model_metrics.r2.toFixed(2)} on held-out test data \u00B7 estimate, not a live quote`;

    const budget = data.budget;
    const estimate = data.estimated_cost;
    const maxVal = Math.max(budget, estimate) || 1;

    document.getElementById("val-budget").textContent = rupee(budget);
    document.getElementById("val-estimate").textContent = rupee(estimate);
    animateBar(document.getElementById("bar-budget"), (budget / maxVal) * 100);
    animateBar(document.getElementById("bar-estimate"), (estimate / maxVal) * 100);

    const verdict = document.getElementById("cost-verdict");
    verdict.textContent = data.within_budget
      ? `Comfortably within budget \u2014 about ${rupee(budget - estimate)} of headroom.`
      : `Running about ${rupee(estimate - budget)} over your stated budget \u2014 see the notes below for ways to trim it.`;
    verdict.style.color = data.within_budget ? "var(--green)" : "var(--coral)";

    const breakdownList = document.getElementById("breakdown-list");
    breakdownList.innerHTML = "";
    Object.entries(data.budget_breakdown).forEach(([category, amount]) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="breakdown-cat">${category}</span><span class="breakdown-amt">${rupee(amount)}</span>`;
      breakdownList.appendChild(li);
    });

    const itineraryList = document.getElementById("itinerary-list");
    itineraryList.innerHTML = "";
    data.itinerary.forEach((day) => {
      const card = document.createElement("div");
      card.className = "day-card";
      card.innerHTML = `
        <div class="day-num">DAY<br>${String(day.day).padStart(2, "0")}</div>
        <div>
          <div class="day-theme">${day.theme}</div>
          <div class="day-slots">
            <div><span class="day-slot-label">Morning</span><span class="day-slot-text">${day.morning}</span></div>
            <div><span class="day-slot-label">Afternoon</span><span class="day-slot-text">${day.afternoon}</span></div>
            <div><span class="day-slot-label">Evening</span><span class="day-slot-text">${day.evening}</span></div>
          </div>
        </div>`;
      itineraryList.appendChild(card);
    });

    const tipsList = document.getElementById("tips-list");
    tipsList.innerHTML = "";
    data.tips.forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = tip;
      tipsList.appendChild(li);
    });

    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const destination = document.getElementById("destination").value;
    const days = document.getElementById("days").value;
    const budget = document.getElementById("budget").value;
    const style = form.querySelector('input[name="style"]:checked').value;

    if (!destination) {
      showError("Pick a destination to continue.");
      return;
    }
    if (!days || Number(days) < 1 || Number(days) > 21) {
      showError("Days should be between 1 and 21.");
      return;
    }
    if (!budget || Number(budget) < 1000) {
      showError("Budget should be at least \u20B91,000.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination, days, budget, style }),
      });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Something went wrong. Please try again.");
        return;
      }
      renderResults(data);
    } catch (err) {
      showError("Couldn't reach the planner. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  });

  replanBtn.addEventListener("click", () => {
    resultsSection.hidden = true;
    document.getElementById("planner-card").scrollIntoView({ behavior: "smooth", block: "center" });
  });

  printBtn.addEventListener("click", () => window.print());
})();
