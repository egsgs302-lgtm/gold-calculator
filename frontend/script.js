document.getElementById("goldForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = document.getElementById("date").value;
  const amount = document.getElementById("amount").value;

  const res = await fetch(`/gold?date=${date}&amount_try=${amount}`);
  const data = await res.json();

  document.getElementById("result").innerText =
    `On ${data.date}, you could buy ${data.grams.toFixed(2)} grams of gold (₺${data.price_per_gram.toFixed(2)} per gram).`;
});
