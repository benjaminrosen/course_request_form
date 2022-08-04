function handleTextChange() {
  const form = document.getElementById("id_form");
  form.setAttribute("action", `${form.action}?{input.value}`);
}

const input = document.getElementById("id_pennkey");
input.addEventListener("input", (event) => handleTextChange(event));
