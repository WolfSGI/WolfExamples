/**
 * FilePond initialisation
 *
 * Looks for every <form data-upload="true"> and converts each
 * <input type="file"> inside it into a FilePond instance.
 * Files are uploaded via PUT and reverted via DELETE on the same URL.
 */
document.addEventListener('DOMContentLoaded', function () {

    // ── init each form ──────────────────────────────────────
    document.querySelectorAll('form[data-upload="true"]').forEach(
        function (form) {
            var formAction = form.getAttribute('action') || window.location.pathname;
            var formMaxSize = parseInt(form.dataset.maxFileSize, 10) || 0;
            var formMaxCount = parseInt(form.dataset.maxFileCount, 10) || 5;

            // Parse existing files for edit mode (once per form)
            var existingFiles = {};
            if (form.dataset.existingFiles) {
                try {
                    existingFiles = JSON.parse(form.dataset.existingFiles);
                } catch (e) {
                    console.warn('fileupload: invalid data-existing-files JSON', e);
                }
            }

            form.querySelectorAll('input[type="file"]').forEach(
                function (input) {
                    var fieldName = input.dataset.name || input.name;
                    if (!fieldName) return;

                    // Per-input overrides
                    var maxSize = parseInt(input.dataset.maxFileSize, 10) || formMaxSize;
                    var maxCount = parseInt(input.dataset.maxFileCount, 10) || formMaxCount;

                    // Build FilePond options
                    var options = {
                        name: fieldName,
                        allowMultiple: maxCount > 1,
                        maxFiles: maxCount,
                        server: {
                            process: {
                                url: formAction,
                                method: 'PUT',
                            },
                            remove: function (uniqueFileId, load, error) {
                                fetch(
                                    formAction
                                        + '/?ticket=' + encodeURIComponent(uniqueFileId),
                                    {method: 'DELETE'}
                                ).then(function (response) {
                                    if (response.ok) {
                                        load();
                                    } else {
                                        error('Fehler beim Entfernen');
                                    }
                                }).catch(function () {
                                    error('Fehler beim Entfernen');
                                });
                            },
                            revert: function (uniqueFileId, load, error) {
                                fetch(
                                    formAction
                                        + '/?ticket=' + encodeURIComponent(uniqueFileId),
                                    {method: 'DELETE'}
                                ).then(function (response) {
                                    if (response.ok) {
                                        load();
                                    } else {
                                        error('Fehler beim Entfernen');
                                    }
                                }).catch(function () {
                                    error('Fehler beim Entfernen');
                                });
                            },
                        },
                    };

                    // ── existing files (edit mode) ───────────────
                    var fieldExisting = existingFiles[fieldName];
                    var removedInput = null;

                    if (fieldExisting && fieldExisting.length) {
                        // Hidden input to track removed existing files
                        removedInput = document.createElement('input');
                        removedInput.type = 'hidden';
                        removedInput.name = fieldName + '_removed';
                        removedInput.value = '[]';
                        form.appendChild(removedInput);

                        // Populate FilePond with existing files as local entries
                        options.files = fieldExisting.map(function (f) {
                            return {
                                source: f.id,
                                options: {
                                    type: 'local',
                                    file: {
                                        name: f.name,
                                        size: f.size,
                                        type: f.type,
                                    },
                                },
                            };
                        });

                        // No-op server.load — files are shown without downloading
                        options.server.load = function (source, load, error, progress, abort) {
                            // Return a fake response so FilePond shows the file
                            load(source);
                            return { abort: function () {} };
                        };

                        // Track removals of existing (LOCAL) files
                        options.onremovefile = function (removeError, file) {
                            if (removeError) return;
                            // FilePond origin 3 = LOCAL
                            if (file.origin !== 3) return;
                            var removed;
                            try {
                                removed = JSON.parse(removedInput.value);
                            } catch (e) {
                                removed = [];
                            }
                            removed.push(file.source);
                            removedInput.value = JSON.stringify(removed);
                        };
                    }
                    FilePond.create(input, options);
                }
            );
        }
    );
});
