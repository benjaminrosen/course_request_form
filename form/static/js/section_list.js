function handleTermChange(event) {
  const submitButton = document.getElementById("id_submit");
  submitButton.click();
}

function addSelectEventListeners() {
  const term = document.getElementById("id_term");
  const status = document.getElementById("id_status");
  const selects = [term, status];
  selects.forEach((select) =>
    select.addEventListener("change", handleTermChange)
  );
}

function focusSearchBar() {
  const search = document.getElementById("id_search");
  search.focus();
}

addSelectEventListeners();
focusSearchBar();
