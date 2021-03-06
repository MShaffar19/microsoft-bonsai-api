/**
 * Code generated by Microsoft (R) AutoRest Code Generator.
 * Changes may cause incorrect behavior and will be lost if the code is
 * regenerated.
 */

package com.microsoft.bonsai.simulatorapi.models;

import java.util.Map;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * The ProblemDetails model.
 */
public class ProblemDetails {
    /**
     * The type property.
     */
    @JsonProperty(value = "type")
    private String type;

    /**
     * The title property.
     */
    @JsonProperty(value = "title")
    private String title;

    /**
     * The status property.
     */
    @JsonProperty(value = "status")
    private Integer status;

    /**
     * The detail property.
     */
    @JsonProperty(value = "detail")
    private String detail;

    /**
     * The instance property.
     */
    @JsonProperty(value = "instance")
    private String instance;

    /**
     * The extensions property.
     */
    @JsonProperty(value = "extensions", access = JsonProperty.Access.WRITE_ONLY)
    private Map<String, Object> extensions;

    /**
     * Get the type value.
     *
     * @return the type value
     */
    public String type() {
        return this.type;
    }

    /**
     * Set the type value.
     *
     * @param type the type value to set
     * @return the ProblemDetails object itself.
     */
    public ProblemDetails withType(String type) {
        this.type = type;
        return this;
    }

    /**
     * Get the title value.
     *
     * @return the title value
     */
    public String title() {
        return this.title;
    }

    /**
     * Set the title value.
     *
     * @param title the title value to set
     * @return the ProblemDetails object itself.
     */
    public ProblemDetails withTitle(String title) {
        this.title = title;
        return this;
    }

    /**
     * Get the status value.
     *
     * @return the status value
     */
    public Integer status() {
        return this.status;
    }

    /**
     * Set the status value.
     *
     * @param status the status value to set
     * @return the ProblemDetails object itself.
     */
    public ProblemDetails withStatus(Integer status) {
        this.status = status;
        return this;
    }

    /**
     * Get the detail value.
     *
     * @return the detail value
     */
    public String detail() {
        return this.detail;
    }

    /**
     * Set the detail value.
     *
     * @param detail the detail value to set
     * @return the ProblemDetails object itself.
     */
    public ProblemDetails withDetail(String detail) {
        this.detail = detail;
        return this;
    }

    /**
     * Get the instance value.
     *
     * @return the instance value
     */
    public String instance() {
        return this.instance;
    }

    /**
     * Set the instance value.
     *
     * @param instance the instance value to set
     * @return the ProblemDetails object itself.
     */
    public ProblemDetails withInstance(String instance) {
        this.instance = instance;
        return this;
    }

    /**
     * Get the extensions value.
     *
     * @return the extensions value
     */
    public Map<String, Object> extensions() {
        return this.extensions;
    }

}
