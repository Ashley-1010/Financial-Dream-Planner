const roles=["Web Developer","Technical Support Engineer","Project Coordinator","Software Engineer","UI UX Designer","QA Engineer","Business Analyst","DevOps Engineer","Data Analyst","Data Scientist"];
roles.forEach(r=>role.add(new Option(r,r)));
fetch("/api/cities").then(r=>r.json()).then(d=>{d.cities.forEach(c=>city.add(new Option(c,c)))});
resultBox.innerHTML = data.salary.predicted_salary;
function money(n){return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(n)}
async function calculate(){
 error.textContent="";
 const payload={age:+age.value,city:city.value,education:education.value,job_role:role.value,saving_percentage:+saving.value,
 goals:[["Marriage",+marriage.value],["Car",+car.value],["Home",+home.value]].map(([goal,years])=>({goal,years}))};
 const res=await fetch("/api/plan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const data=await res.json();
 if(!res.ok){error.textContent=data.detail||"Invalid input";return}
 results.classList.remove("hidden");
 let html=`<div class="result-grid"><div><b>Predicted monthly salary</b><div class="metric">${money(data.salary_prediction)}</div></div><div><b>Total monthly investment</b><div class="metric">${money(data.total_monthly_required)}</div></div><div><b>Available capacity</b><div class="metric">${money(data.feasibility.available_capacity)}</div></div></div><hr>`;
 data.goals.forEach(g=>{html+=`<div class="goal"><h3>${g.goal}</h3><p>Timeline: ${g.timeline_years} years • ${g.category}</p><p>Current cost: <b>${money(g.current_cost)}</b></p><p>Future cost at 6% inflation: <b>${money(g.future_cost)}</b></p><p>Required monthly investment: <b>${money(g.monthly_investment)}</b></p><p>Assumed return: ${(g.assumed_annual_return*100).toFixed(0)}%/year</p></div>`});
 const f=data.feasibility; const cls=f.surplus_or_shortfall>=0?"good":"bad"; const label=f.surplus_or_shortfall>=0?"Surplus":"Shortfall";
 html+=`<div class="status ${cls}"><b>${f.status}</b><br>${label}: ${money(Math.abs(f.surplus_or_shortfall))}<br>Saving target: ${f.saving_percentage}%</div>`;
 output.innerHTML=html;
}
async function askAgent(){agentOutput.textContent="Thinking...";const res=await fetch("/api/agent",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:agentText.value})});agentOutput.textContent=JSON.stringify(await res.json(),null,2)}
