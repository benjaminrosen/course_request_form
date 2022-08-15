import { getElementByRowCount } from "./row_count.js"
import { handleLoadOrEditButton } from "./load_or_edit_button.js"
import { handleEnabledInput } from "./enabled_input.js"
import { handleDisabledInput } from "./disabled_input.js"

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
  const mutationConfig = { childList: true };
  autoAddObserver.observe(formDiv, mutationConfig);
}
