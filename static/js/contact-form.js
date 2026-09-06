/*
 * Contact form validation.
 *
 * This is progressive enhancement only: the form has `novalidate` on it so
 * we can show inline, editorially-worded errors instead of the browser's
 * default validation bubbles. If this script fails to load for any reason,
 * the form still posts normally and Django's server-side ContactForm
 * validates it — nothing here is required for correctness.
 */
(function () {
  "use strict";

  // Mirrors the wording used server-side in newsroom/forms.py so the
  // message reads the same whether it's caught by the browser or by Django.
  var MESSAGES = {
    name: {
      valueMissing: "Please tell us who's writing in.",
    },
    email: {
      valueMissing: "We'll need an address to write back to.",
      typeMismatch: "That doesn't look like a deliverable address — please check it.",
    },
    subject: {
      valueMissing: "Give your message a headline of its own.",
    },
    message: {
      valueMissing: "The message field is looking a little empty.",
    },
  };

  function messageFor(field) {
    var rules = MESSAGES[field.name];
    if (rules) {
      if (field.validity.valueMissing && rules.valueMissing) {
        return rules.valueMissing;
      }
      if (field.validity.typeMismatch && rules.typeMismatch) {
        return rules.typeMismatch;
      }
    }
    return field.validationMessage;
  }

  function clearError(field) {
    var existing = document.getElementById(field.id + "_client_error");
    if (existing && existing.parentNode) {
      existing.parentNode.removeChild(existing);
    }
    field.removeAttribute("aria-invalid");
  }

  function showError(field, text) {
    clearError(field);
    var note = document.createElement("p");
    note.className = "field-error";
    note.id = field.id + "_client_error";
    note.setAttribute("role", "alert");
    note.textContent = text;
    field.insertAdjacentElement("afterend", note);
    field.setAttribute("aria-invalid", "true");
  }

  function init() {
    var form = document.querySelector(".contact-form");
    if (!form) return;

    var fields = Array.prototype.slice.call(
      form.querySelectorAll(".field-input")
    );

    fields.forEach(function (field) {
      field.addEventListener("input", function () {
        if (field.checkValidity()) {
          clearError(field);
        }
      });
    });

    form.addEventListener("submit", function (event) {
      var firstInvalid = null;

      fields.forEach(function (field) {
        clearError(field);
        if (!field.checkValidity()) {
          showError(field, messageFor(field));
          firstInvalid = firstInvalid || field;
        }
      });

      if (firstInvalid) {
        event.preventDefault();
        firstInvalid.focus();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
