import { getNext } from "./user_row.js";

function getActiveSortValue(parameters) {
  const parameterValues = getParameterValues(parameters);
  return parameterValues.sort;
}

function getParametersFromButton() {
  const activeSortButton = document.getElementsByClassName("sort-active")[0];
  const url = activeSortButton.getAttribute("hx-get");
  return url.split("?")[1];
}

function isActiveSort(sort) {
  const parameters = getParametersFromButton();
  const activeSortValue = getActiveSortValue(parameters);
  return sort == activeSortValue;
}

function reverseOrder(sort) {
  if (sort.includes("-")) {
    return sort.replace("-", "");
  }
  return `-${sort}`;
}

function getParameterValues(parameters) {
  const keyValuePairs = parameters.split("&");
  const parameterValues = {};
  keyValuePairs.forEach((keyAndValue) => {
    let [key, value] = keyAndValue.split("=");
    parameterValues[key] = value;
  });
  return parameterValues;
}

function getTerm() {
  const select = document.getElementById("id_term");
  return select.value;
}

function getStatus() {
  const select = document.getElementById("id_status");
  return select.value;
}

function getSearch() {
  const select = document.getElementById("id_search");
  return select.value;
}

function getParameterString(parameters) {
  parameters.term = getTerm();
  parameters.status = getStatus();
  parameters.search = getSearch();
  const keyValueStrings = [];
  for (let [key, value] of Object.entries(parameters)) {
    if (key == "sort" && isActiveSort(value)) {
      value = reverseOrder(value);
    }
    const keyValueString = `${key}=${value}`;
    keyValueStrings.push(keyValueString);
  }
  return keyValueStrings.join("&");
}

function setPageButtonParameters(button, parameters) {
  parameters = getParameterString(parameters);
  const hrefBase = button.href.split("&")[0];
  button.href = `${hrefBase}&${parameters}`;
}

function updatePageButtonHrefs() {
  let parameters = getParametersFromButton();
  parameters = getParameterValues(parameters);
  const pageButtons = [...document.getElementsByClassName("page_button")];
  pageButtons.forEach((button) => setPageButtonParameters(button, parameters));
}

function hideFirstAndPrevious() {
  const first = getNext(document.querySelectorAll("[id^='id_first']"));
  const previous = getNext(document.querySelectorAll("[id^='id_previous']"));
  const next = getNext(document.querySelectorAll("[id^='id_next']"));
  const last = getNext(document.querySelectorAll("[id^='id_last']"));
  if (first && previous) {
    [first, previous].forEach((element) => {
      element.style.display = "none";
    });
  }
  if (next && last) {
    const pageRegex = /page=\d+/;
    next.href = next.href.replace(pageRegex, "page=2");
    const currentPage = document.getElementById("current");
    const total = parseInt(currentPage.innerHTML.split("of ")[1]);
    last.href = last.href.replace(pageRegex, `page=${total}`);
    currentPage.innerHTML = `Page 1 of ${total}`;
  }
}

function updatePage() {
  updatePageButtonHrefs();
  hideFirstAndPrevious();
}

export function addSectionListObserver() {
  const sectionListObserver = new MutationObserver(updatePage);
  const sectionListDiv = document.getElementById("id_section_list");
  const mutationConfig = { childList: true };
  sectionListObserver.observe(sectionListDiv, mutationConfig);
}
