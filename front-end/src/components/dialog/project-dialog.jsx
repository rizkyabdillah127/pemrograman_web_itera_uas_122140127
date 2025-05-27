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
import { useProjects } from "@/hooks/useProjects";

export default function ProjectDialog({
  triggerText,
  open,
  onOpenChange,
  initialData,
  isEdit,
}) {
  const { createProject, updateProject } = useProjects();

  const [formData, setFormData] = useState(
    initialData || {
      name: "",
      description: "",
      start_date: format(new Date(), "yyyy-MM-dd"),
      ends_date: format(new Date(), "yyyy-MM-dd"),
      status: "planning",
    }
  );

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleDateSelect = (field) => (date) => {
    setFormData((prev) => ({
      ...prev,
      [field]: format(date, "yyyy-MM-dd"),
    }));
  };

  const handleSubmit = async () => {
    const { name, description } = formData;

    if (!name || !description) {
      toast.error("Name and description are required.");
      return;
    }

    const action = isEdit ? updateProject : createProject;
    const result = await action(formData);

    if (result?.success) {
      toast.success(isEdit ? "Project updated!" : "Project created!");

      // timeout 1s to reload the page
      setTimeout(() => {
        window.location.reload();
      }, 1000);

      onOpenChange(false);
    } else {
      toast.error(
        `${isEdit ? "Update" : "Create"} failed: ${
          result?.message || "Unknown error"
        }`
      );
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogTrigger asChild>
        <Button>{triggerText}</Button>
      </AlertDialogTrigger>
      <AlertDialogContent className="max-w-lg w-full p-6">
        <AlertDialogHeader>
          <AlertDialogTitle>
            {isEdit ? "Edit Project" : "Create New Project"}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {isEdit
              ? "Update the details below to edit this project."
              : "Fill in the details below to create a new project."}
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-4 mt-4">
          {[
            {
              label: "Project Name",
              name: "name",
              placeholder: "Enter project name",
            },
            {
              label: "Description",
              name: "description",
              placeholder: "Enter project description",
            },
          ].map(({ label, name, placeholder }) => (
            <div className="space-y-2" key={name}>
              <Label htmlFor={name}>{label}</Label>
              <Input
                id={name}
                name={name}
                placeholder={placeholder}
                value={formData[name]}
                onChange={handleChange}
              />
            </div>
          ))}

          <div className="grid grid-cols-2 gap-4">
            {["start_date", "ends_date"].map((field) => (
              <div className="space-y-2" key={field}>
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
                      {formData[field]}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={new Date(formData[field])}
                      onSelect={handleDateSelect(field)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            ))}
          </div>

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
                <SelectItem value="planning">Planning</SelectItem>
                <SelectItem value="ongoing">Ongoing</SelectItem>
                <SelectItem value="finished">Finished</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <AlertDialogFooter className="mt-6">
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleSubmit}>
            {isEdit ? "Save Changes" : "Create Project"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

ProjectDialog.propTypes = {
  triggerText: PropTypes.string.isRequired,
  open: PropTypes.bool.isRequired,
  onOpenChange: PropTypes.func.isRequired,
  initialData: PropTypes.shape({
    name: PropTypes.string,
    description: PropTypes.string,
    start_date: PropTypes.string,
    ends_date: PropTypes.string,
    status: PropTypes.string,
  }),
  isEdit: PropTypes.bool,
};

ProjectDialog.defaultProps = {
  initialData: null,
  isEdit: false,
};
