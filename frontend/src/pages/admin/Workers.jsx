// src/pages/admin/Workers.jsx

import { useMemo, useState } from "react";

import {
  AlertCircle,
  Camera,
  CheckCircle2,
  Eye,
  MoreVertical,
  Pencil,
  Plus,
  Search,
  Trash2,
  Upload,
  UserPlus,
  X,
} from "lucide-react";

import { useWorkers } from "../../hooks/useWorkers";

function normalizeWorker(worker) {
  return {
    ...worker,

    id:
      worker?.worker_id ??
      worker?.id ??
      null,

    name:
      worker?.name ??
      "Unnamed Worker",

    employeeId:
      worker?.employee_id ??
      worker?.employeeId ??
      "—",

    role:
      worker?.role ??
      "—",

    department:
      worker?.department ??
      "—",

    tagId:
      worker?.tag_id ??
      worker?.tagId ??
      "—",

    status:
      worker?.status ??
      (worker?.is_active === false ? "Inactive" : "Active"),

    compliance:
      worker?.ppe_compliance ??
      worker?.ppeCompliance ??
      null,
  };
}

function Modal({ title, children, onClose }) {
  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">
            {title}
          </h2>

          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  required = false,
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        {label}
        {required && (
          <span className="text-red-500 ml-1">*</span>
        )}
      </label>

      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      />
    </div>
  );
}

function CreateWorkerModal({
  onClose,
  onSubmit,
  saving,
  apiError,
}) {
  const [form, setForm] = useState({
    name: "",
    employee_id: "",
    role: "",
    department: "",
    tag_id: "",
  });

  const [faceImages, setFaceImages] =
    useState([]);

  const [localError, setLocalError] =
    useState("");

  const handleFaceImagesChange = (event) => {
    const selectedFiles = Array.from(
      event.target.files || []
    );

    setFaceImages((currentFiles) => {
      const files = [...currentFiles, ...selectedFiles];
      const uniqueFiles = files.filter(
        (file, index, allFiles) =>
          allFiles.findIndex(
            (candidate) =>
              candidate.name === file.name &&
              candidate.size === file.size &&
              candidate.lastModified === file.lastModified
          ) === index
      );

      if (uniqueFiles.length > 5) {
        setLocalError(
          "You can select a maximum of 5 face images."
        );
      } else {
        setLocalError("");
      }

      return uniqueFiles.slice(0, 5);
    });

    // Allow selecting the same file again after removing it.
    event.target.value = "";
  };

  const removeFaceImage = (fileToRemove) => {
    setFaceImages((currentFiles) =>
      currentFiles.filter((file) => file !== fileToRemove)
    );
    setLocalError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLocalError("");

    if (!form.name.trim()) {
      setLocalError("Name is required.");
      return;
    }

    if (!form.employee_id.trim()) {
      setLocalError(
        "Employee ID is required."
      );
      return;
    }

    if (!form.role.trim()) {
      setLocalError("Role is required.");
      return;
    }

    if (!form.department.trim()) {
      setLocalError(
        "Department is required."
      );
      return;
    }

    if (faceImages.length === 0) {
      setLocalError(
        "At least one face image is required."
      );
      return;
    }

    try {
      await onSubmit({
        ...form,
        face_images: faceImages,
      });

      onClose();
    } catch {
      // Hook/API error is displayed below.
    }
  };

  return (
    <Modal
      title="Add Worker"
      onClose={saving ? () => { } : onClose}
    >
      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >
        {(localError || apiError) && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 flex gap-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />

            <span>
              {localError ||
                apiError?.message ||
                "Failed to create worker."}
            </span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field
            label="Name"
            required
            value={form.name}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                name: e.target.value,
              }))
            }
            placeholder="John Doe"
          />

          <Field
            label="Employee ID"
            required
            value={form.employee_id}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                employee_id: e.target.value,
              }))
            }
            placeholder="EMP-001"
          />

          <Field
            label="Role"
            required
            value={form.role}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                role: e.target.value,
              }))
            }
            placeholder="Construction Worker"
          />

          <Field
            label="Department"
            required
            value={form.department}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                department: e.target.value,
              }))
            }
            placeholder="Construction"
          />

          <Field
            label="Tag ID"
            value={form.tag_id}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                tag_id: e.target.value,
              }))
            }
            placeholder="Optional"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Face Images
            <span className="text-red-500 ml-1">
              *
            </span>
          </label>

          <label className="border-2 border-dashed border-gray-300 rounded-xl p-5 flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/40 transition-colors">
            <input
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={handleFaceImagesChange}
            />

            <Upload className="h-7 w-7 text-blue-500 mb-2" />

            <p className="text-sm font-medium text-gray-700">
              Select face image(s)
            </p>

            <p className="text-xs text-gray-400 mt-1">
              Select 3 to 5 images
            </p>
          </label>

          {faceImages.length > 0 && (
            <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-3">
              {faceImages.map(
                (file, index) => (
                  <div
                    key={`${file.name}-${index}`}
                    className="relative overflow-hidden rounded-lg border border-gray-200 bg-gray-50"
                  >
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      className="h-24 w-full object-cover"
                    />
                    <button
                      type="button"
                      onClick={() => removeFaceImage(file)}
                      className="absolute top-1 right-1 rounded-full bg-black/60 p-1 text-white hover:bg-black/80"
                      aria-label={`Remove ${file.name}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                    <p className="truncate px-2 py-1 text-xs text-gray-500">
                      {file.name}
                    </p>
                  </div>
                )
              )}
            </div>
          )}

          <p className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <Camera className="h-3.5 w-3.5" />
            {faceImages.length} of 5 images selected
          </p>
        </div>

        <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:bg-blue-400 flex items-center gap-2"
          >
            {saving ? (
              "Creating..."
            ) : (
              <>
                <UserPlus className="h-4 w-4" />
                Create Worker
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function EditWorkerModal({
  worker,
  onClose,
  onSubmit,
  saving,
  apiError,
}) {
  const normalized = normalizeWorker(worker);

  const [form, setForm] = useState({
    name: normalized.name === "Unnamed Worker"
      ? ""
      : normalized.name,
    employee_id:
      normalized.employeeId === "—"
        ? ""
        : normalized.employeeId,
    role:
      normalized.role === "—"
        ? ""
        : normalized.role,
    department:
      normalized.department === "—"
        ? ""
        : normalized.department,
    tag_id:
      normalized.tagId === "—"
        ? ""
        : normalized.tagId,
  });

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      await onSubmit(worker.worker_id ?? worker.id, {
        name: form.name,
        employee_id: form.employee_id,
        role: form.role,
        department: form.department,
        tag_id: form.tag_id,
      });

      onClose();
    } catch {
      // Hook/API error is displayed below.
    }
  };

  return (
    <Modal
      title="Edit Worker"
      onClose={saving ? () => { } : onClose}
    >
      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >
        {apiError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 flex gap-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />

            <span>
              {apiError.message ||
                "Failed to update worker."}
            </span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field
            label="Name"
            required
            value={form.name}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                name: e.target.value,
              }))
            }
          />

          <Field
            label="Employee ID"
            required
            value={form.employee_id}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                employee_id: e.target.value,
              }))
            }
          />

          <Field
            label="Role"
            required
            value={form.role}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                role: e.target.value,
              }))
            }
          />

          <Field
            label="Department"
            required
            value={form.department}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                department: e.target.value,
              }))
            }
          />

          <Field
            label="Tag ID"
            value={form.tag_id}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                tag_id: e.target.value,
              }))
            }
          />
        </div>

        <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:bg-blue-400 flex items-center gap-2"
          >
            <Pencil className="h-4 w-4" />

            {saving
              ? "Saving..."
              : "Save Changes"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default function Workers() {
  const {
    workers,
    loading,
    saving,
    deleting,
    error,
    create,
    update,
    remove,
    getDetails,
    loadWorkers,
  } = useWorkers();

  const [search, setSearch] =
    useState("");

  const [showCreate, setShowCreate] =
    useState(false);

  const [editingWorker, setEditingWorker] =
    useState(null);

  const [viewingWorker, setViewingWorker] =
    useState(null);

  const [actionWorkerId, setActionWorkerId] =
    useState(null);

  const [deleteConfirm, setDeleteConfirm] =
    useState(null);

  const filteredWorkers = useMemo(() => {
    const query = search
      .trim()
      .toLowerCase();

    if (!query) {
      return workers;
    }

    return workers.filter((worker) => {
      const normalized =
        normalizeWorker(worker);

      return [
        normalized.name,
        normalized.employeeId,
        normalized.role,
        normalized.department,
        normalized.tagId,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value)
            .toLowerCase()
            .includes(query)
        );
    });
  }, [workers, search]);

  const handleView = async (worker) => {
    try {
      const details = await getDetails(
        worker.worker_id ?? worker.id
      );

      setViewingWorker(details);
    } catch {
      // Error is already held by the hook.
    } finally {
      setActionWorkerId(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) {
      return;
    }

    try {
      await remove(
        deleteConfirm.worker_id ??
        deleteConfirm.id
      );

      setDeleteConfirm(null);
    } catch {
      // Hook keeps the error.
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex sm:items-center justify-between flex-col sm:flex-row gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Worker Management
          </h1>

          <p className="text-sm text-gray-500 mt-1">
            Manage personnel, roles, and worker
            profiles.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Worker
        </button>
      </div>

      {/* API error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />

            <span>
              {error.message ||
                "Failed to communicate with the backend."}
            </span>
          </div>

          <button
            type="button"
            onClick={loadWorkers}
            className="text-sm font-semibold underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div className="relative max-w-sm w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />

            <input
              type="text"
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search workers..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          <span className="hidden sm:block text-xs text-gray-400">
            {filteredWorkers.length} worker
            {filteredWorkers.length === 1
              ? ""
              : "s"}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50/50 text-gray-500 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">
                  Name
                </th>

                <th className="px-6 py-4 font-semibold">
                  Role
                </th>

                <th className="px-6 py-4 font-semibold">
                  Department
                </th>

                <th className="px-6 py-4 font-semibold">
                  Status
                </th>

                <th className="px-6 py-4 font-semibold">
                  Compliance
                </th>

                <th className="px-6 py-4 font-semibold text-right">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100 text-sm">
              {loading ? (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-10 text-center text-gray-500"
                  >
                    Loading workers...
                  </td>
                </tr>
              ) : filteredWorkers.length === 0 ? (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-12 text-center"
                  >
                    <div className="flex flex-col items-center">
                      <UserPlus className="h-10 w-10 text-gray-300 mb-3" />

                      <p className="font-medium text-gray-700">
                        No workers found
                      </p>

                      <p className="text-sm text-gray-400 mt-1">
                        {search
                          ? "Try another search."
                          : "Add your first worker."}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredWorkers.map(
                  (worker) => {
                    const item =
                      normalizeWorker(
                        worker
                      );

                    const compliance =
                      typeof item.compliance ===
                        "number"
                        ? Math.max(
                          0,
                          Math.min(
                            100,
                            item.compliance
                          )
                        )
                        : null;

                    return (
                      <tr
                        key={item.id}
                        className="hover:bg-gray-50 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900">
                              {item.name}
                            </p>

                            <p className="text-xs text-gray-400 mt-0.5">
                              {item.employeeId}
                            </p>
                          </div>
                        </td>

                        <td className="px-6 py-4 text-gray-500">
                          {item.role}
                        </td>

                        <td className="px-6 py-4 text-gray-500">
                          {item.department}
                        </td>

                        <td className="px-6 py-4">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {item.status ||
                              "Registered"}
                          </span>
                        </td>

                        <td className="px-6 py-4">
                          {compliance !== null ? (
                            <div className="flex items-center">
                              <div className="w-full bg-gray-200 rounded-full h-2 mr-2 max-w-[4rem]">
                                <div
                                  className={`h-2 rounded-full ${compliance >= 90
                                      ? "bg-green-500"
                                      : compliance > 50
                                        ? "bg-yellow-500"
                                        : "bg-red-500"
                                    }`}
                                  style={{
                                    width: `${compliance}%`,
                                  }}
                                />
                              </div>

                              <span className="text-xs text-gray-500">
                                {compliance}%
                              </span>
                            </div>
                          ) : (
                            <span className="text-xs text-gray-400">
                              —
                            </span>
                          )}
                        </td>

                        <td className="px-6 py-4 text-right relative">
                          <button
                            type="button"
                            onClick={() =>
                              setActionWorkerId(
                                actionWorkerId ===
                                  item.id
                                  ? null
                                  : item.id
                              )
                            }
                            className="text-gray-400 hover:text-gray-600 transition-colors"
                          >
                            <MoreVertical className="h-5 w-5 ml-auto" />
                          </button>

                          {actionWorkerId ===
                            item.id && (
                              <div className="absolute right-6 top-12 z-20 bg-white border border-gray-200 rounded-lg shadow-lg w-44 py-1 text-left">
                                <button
                                  type="button"
                                  onClick={() =>
                                    handleView(
                                      worker
                                    )
                                  }
                                  className="w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                                >
                                  <Eye className="h-4 w-4" />
                                  View details
                                </button>

                                <button
                                  type="button"
                                  onClick={() => {
                                    setEditingWorker(
                                      worker
                                    );
                                    setActionWorkerId(
                                      null
                                    );
                                  }}
                                  className="w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                                >
                                  <Pencil className="h-4 w-4" />
                                  Edit worker
                                </button>

                                <button
                                  type="button"
                                  onClick={() => {
                                    setDeleteConfirm(
                                      worker
                                    );
                                    setActionWorkerId(
                                      null
                                    );
                                  }}
                                  className="w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                                >
                                  <Trash2 className="h-4 w-4" />
                                  Delete worker
                                </button>
                              </div>
                            )}
                        </td>
                      </tr>
                    );
                  }
                )
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create */}
      {showCreate && (
        <CreateWorkerModal
          onClose={() => setShowCreate(false)}
          onSubmit={create}
          saving={saving}
          apiError={error}
        />
      )}

      {/* Edit */}
      {editingWorker && (
        <EditWorkerModal
          worker={editingWorker}
          onClose={() =>
            setEditingWorker(null)
          }
          onSubmit={update}
          saving={saving}
          apiError={error}
        />
      )}

      {/* View details */}
      {viewingWorker && (
        <Modal
          title="Worker Details"
          onClose={() =>
            setViewingWorker(null)
          }
        >
          {(() => {
            const worker =
              normalizeWorker(
                viewingWorker
              );

            return (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Name
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.name}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Employee ID
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.employeeId}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Role
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.role}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Department
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.department}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Tag ID
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.tagId}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase">
                      Status
                    </p>
                    <p className="font-medium text-gray-900 mt-1">
                      {worker.status ||
                        "Registered"}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() =>
                    setViewingWorker(null)
                  }
                  className="w-full mt-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
                >
                  Close
                </button>
              </div>
            );
          })()}
        </Modal>
      )}

      {/* Delete confirmation */}
      {deleteConfirm && (
        <Modal
          title="Delete Worker"
          onClose={() =>
            deleting
              ? null
              : setDeleteConfirm(null)
          }
        >
          <div className="space-y-5">
            <div className="p-4 bg-red-50 border border-red-100 rounded-xl">
              <p className="text-sm text-red-700">
                Are you sure you want to delete{" "}
                <strong>
                  {
                    normalizeWorker(
                      deleteConfirm
                    ).name
                  }
                </strong>
                ?
              </p>

              <p className="text-xs text-red-500 mt-1">
                This action will be sent to the
                backend and cannot be undone from
                this page.
              </p>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() =>
                  setDeleteConfirm(null)
                }
                disabled={deleting}
                className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleDelete}
                disabled={deleting}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg text-sm font-medium flex items-center gap-2"
              >
                <Trash2 className="h-4 w-4" />

                {deleting
                  ? "Deleting..."
                  : "Delete Worker"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}