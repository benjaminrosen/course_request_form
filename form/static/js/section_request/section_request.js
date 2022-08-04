import { addExcludeAnnouncementsListeners } from "./exclude_announcements_listeners.js";
import { addCreateRowListener } from "../create_row_listener.js";
import { addEnterKeyListener } from "../enter_key_listener.js";
import { addObserver } from "../observer.js"

addExcludeAnnouncementsListeners();
addCreateRowListener("id_add_enrollment");
addObserver("id_additional_enrollments_form");
addEnterKeyListener();
