function addListeners() {
  const loadUserButton = getElementByRowCount("id_load_user");
  const editUserButton = getElementByRowCount("id_edit");
  const loadOrEditButton = loadUserButton || editUserButton;
  const enabledInput = getElementByRowCount("id_user");
  const disabledInput = getElementByRowCount("id_pennkey");
  handleLoadOrEditButton(loadOrEditButton);
  handleEnabledInput(enabledInput);
  handleDisabledInput(disabledInput);
}

export function addObserver(formId) {
  const autoAddObserver = new MutationObserver(addListeners);
  const formDiv = document.getElementById(formId);
  console.log(formDiv)
  const mutationConfig = { childList: true };
  autoAddObserver.observe(formDiv, mutationConfig);
}
