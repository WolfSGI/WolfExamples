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
            document.querySelectorAll('[role="existingFiles"]').forEach(
                function (el) {
                    const newData = JSON.parse(el.textContent);
                    existingFiles = {...existingFiles,...newData}
                }
            );

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
                                        error('Error during deletion.');
                                    }
                                }).catch(function () {
                                    error('Error during deletion.');
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
                                        error('Error during deletion.');
                                    }
                                }).catch(function () {
                                    error('Error during deletion.');
                                });
                            },
                        },
                    };

                    // ── existing files (edit mode) ───────────────
                    var fieldExisting = existingFiles[fieldName];
                    if (fieldExisting && fieldExisting.length) {
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
                    }
                    FilePond.create(input, options);
                }
            );
        }
    );
});
