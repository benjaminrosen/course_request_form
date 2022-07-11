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

function getPageButtons() {
  const first = document.getElementById("id_first");
  const previous = document.getElementById("id_previous");
  const next = document.getElementById("id_next");
  const last = document.getElementById("id_last");
  const pageButtons = [first, previous, next, last];
  return pageButtons.filter((button) => !!button);
}

function removePageFromQuery(query) {
  let parameters = query.split("&");
  parameters = parameters.filter((parameter) => !parameter.includes("page="));
  return parameters.join("&");
}

function setHrefParameters(button, query) {
  const [baseUrl, pageNumber] = button.href.split("?");
  button.href = `${baseUrl}?${pageNumber}&${query}`;
}

function addPageButtonListeners() {
  const pageButtons = getPageButtons();
  let query = window.location.search.slice(1);
  query = removePageFromQuery(query);
  pageButtons.forEach((button) => setHrefParameters(button, query));
}

addSelectEventListeners();
focusSearchBar();
addPageButtonListeners();

function addListeners() {
  const loadUserButton = getElementByEnrollmentCount("id_load_user");
  handleDisabledInput(disabledInput);
}

export function addSectionListbserver() {
  const sectionListObserver = new MutationObserver(addListeners);
  const sectionListDiv = document.getElementById("id_section_list");
  const mutationConfig = { childList: true };
  sectionListObserver.observe(sectionListDiv, mutationConfig);
}
