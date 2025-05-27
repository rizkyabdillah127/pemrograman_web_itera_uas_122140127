import React, { useState } from "react";
import PropTypes from "prop-types";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import { useTasks } from "@/hooks/useTasks";

export default function TaskDialog({
  triggerText,
  open,
  onOpenChange,
  initialData,
  isEdit,
  projectId,
}) {
  const { createTask, updateTask } = useTasks();
  const [formData, setFormData] = useState(
    initialData || {
      name: "",
      description: "",
      start_date: format(new Date(), "yyyy-MM-dd"),
      ends_date: format(new Date(), "yyyy-MM-dd"),
      status: "todo",
      project_id: projectId,
    }
  );

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleDateSelect = (field, date) => {
    setFormData((prev) => ({
      ...prev,
      [field]: date ? format(date, "yyyy-MM-dd") : "",
    }));
  };

  const handleSubmit = async () => {
    const { name, description } = formData;

    if (!name || !description) {
      toast.error("Name and description are required.");
      return;
    }

    const action = isEdit ? updateTask : createTask;
    const result = await action(formData);

    if (result?.success) {
      toast.success(isEdit ? "Task updated!" : "Task created!");

      // timeout 1s to reload the page
      setTimeout(() => {
        window.location.reload();
      }, 1000);

      onOpenChange(false);
    } else {
      toast.error(result?.message || "An error occurred.");
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogTrigger asChild>{triggerText}</AlertDialogTrigger>
      <AlertDialogContent className="max-w-lg w-full p-6 bg-white dark:bg-gray-900 rounded-lg shadow-lg">
        <AlertDialogHeader>
          <AlertDialogTitle>
            {isEdit ? "Edit Task" : "Create New Task"}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {isEdit
              ? "Update the details below to edit this task."
              : "Fill in the details below to create a new task."}
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-4 mt-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Task Name</Label>
            <Input
              id="name"
              name="name"
              placeholder="Enter task name"
              value={formData.name}
              onChange={handleChange}
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              name="description"
              placeholder="Enter task description"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          {/* Date Pickers */}
          <div className="grid grid-cols-2 gap-4">
            {["start_date", "ends_date"].map((field) => (
              <div key={field} className="space-y-2">
                <Label>
                  {field === "start_date" ? "Start Date" : "End Date"}
                </Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal"
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {formData[field] || "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={
                        formData[field] ? new Date(formData[field]) : undefined
                      }
                      onSelect={(date) => handleDateSelect(field, date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            ))}
          </div>

          {/* Status */}
          <div className="space-y-2">
            <Label>Status</Label>
            <Select
              value={formData.status}
              onValueChange={(value) =>
                setFormData((prev) => ({ ...prev, status: value }))
              }
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todo">Todo</SelectItem>
                <SelectItem value="not started">Not Started</SelectItem>
                <SelectItem value="in progress">In Progress</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="finished">Finished</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <AlertDialogFooter className="mt-6">
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleSubmit}>
            {isEdit ? "Save Changes" : "Create Task"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

TaskDialog.propTypes = {
  triggerText: PropTypes.node.isRequired,
  open: PropTypes.bool.isRequired,
  onOpenChange: PropTypes.func.isRequired,
  initialData: PropTypes.shape({
    name: PropTypes.string,
    description: PropTypes.string,
    start_date: PropTypes.string,
    ends_date: PropTypes.string,
    status: PropTypes.string,
    project_id: PropTypes.string,
  }),
  isEdit: PropTypes.bool,
  projectId: PropTypes.string,
};

TaskDialog.defaultProps = {
  initialData: null,
  isEdit: false,
};
