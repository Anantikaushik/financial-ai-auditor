import streamlit as st

from backend.services.upload_service import UploadService


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Financial AI Auditor",
    page_icon="💰",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "service" not in st.session_state:
    st.session_state.service = UploadService()

if "result" not in st.session_state:
    st.session_state.result = None


service = st.session_state.service


# ============================================================
# HEADER
# ============================================================

st.title("💰 Financial AI Auditor")

st.markdown(
    """
    Upload a financial document and the system will:

    **Extract → Validate → Audit → Detect Financial Anomalies**
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a financial document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg",
        ],
    )

    st.markdown("---")

    st.caption(
        "Supported formats: PDF, PNG, JPG, JPEG"
    )


# ============================================================
# PROCESS DOCUMENT
# ============================================================

if uploaded_file is not None:

    st.info(
        f"Selected: **{uploaded_file.name}** "
        f"({uploaded_file.size / 1024:.1f} KB)"
    )

    process_button = st.button(
        "🔍 Analyze Financial Document",
        type="primary",
        use_container_width=True,
    )

    if process_button:

        # -----------------------------------------------
        # Read uploaded file
        # -----------------------------------------------

        file_bytes = uploaded_file.getvalue()

        # -----------------------------------------------
        # Processing
        # -----------------------------------------------

        with st.status(
            "Processing financial document...",
            expanded=True,
        ) as status:

            try:

                st.write("📄 Reading document...")

                st.write(
                    "🔎 Extracting financial information..."
                )

                result = service.process(
                    file_bytes=file_bytes,
                    file_name=uploaded_file.name,
                )

                # ---------------------------------------
                # Validate returned structure
                # ---------------------------------------

                if not isinstance(result, dict):

                    raise RuntimeError(
                        "UploadService returned an "
                        "unexpected result."
                    )

                document = result.get(
                    "document"
                )

                audit = result.get(
                    "audit"
                )

                if document is None:

                    raise RuntimeError(
                        "Financial document extraction "
                        "returned no document."
                    )

                if audit is None:

                    raise RuntimeError(
                        "Document extraction completed, "
                        "but the financial audit did not "
                        "return a result."
                    )

                st.write(
                    "🧮 Running deterministic financial audit..."
                )

                st.write(
                    "⚠️ Checking totals, tax, line items "
                    "and missing information..."
                )

                st.session_state.result = result

                status.update(
                    label=(
                        "✅ Document extracted and "
                        "financially audited"
                    ),
                    state="complete",
                    expanded=False,
                )

            except Exception as exc:

                status.update(
                    label="❌ Document processing failed",
                    state="error",
                    expanded=True,
                )

                st.error(
                    f"{type(exc).__name__}: {exc}"
                )

                st.exception(exc)


# ============================================================
# DISPLAY RESULTS
# ============================================================

result = st.session_state.result


if result is not None:

    document = result.get("document")
    audit = result.get("audit")

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if audit is not None:

        finding_count = len(
            audit.findings
        )

        if audit.risk_level == "HIGH":

            st.error(
                f"🔴 Financial audit completed — "
                f"HIGH risk, {finding_count} finding(s)."
            )

        elif audit.risk_level == "MEDIUM":

            st.warning(
                f"🟠 Financial audit completed — "
                f"MEDIUM risk, {finding_count} finding(s)."
            )

        else:

            st.success(
                f"🟢 Financial audit completed — "
                f"LOW risk, {finding_count} finding(s)."
            )


    # ========================================================
    # EXTRACTED FINANCIAL INFORMATION
    # ========================================================

    st.divider()

    st.header(
        "📋 Extracted Financial Information"
    )

    # --------------------------------------------------------
    # Top metrics
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.caption("Vendor")

        st.subheader(
            document.vendor_name
            or "N/A"
        )

    with col2:

        st.caption("Invoice Number")

        st.subheader(
            document.invoice_number
            or "N/A"
        )

    with col3:

        st.caption("Total Amount")

        if (
            document.total_amount
            is not None
        ):

            st.subheader(
                f"{document.currency} "
                f"{document.total_amount}"
            )

        else:

            st.subheader("N/A")

    with col4:

        st.caption("Confidence")

        if (
            document.extraction_confidence
            is not None
        ):

            st.subheader(
                f"{document.extraction_confidence:.0%}"
            )

        else:

            st.subheader("N/A")


    # ========================================================
    # INVOICE DETAILS
    # ========================================================

    with st.expander(
        "🧾 Invoice Details",
        expanded=True,
    ):

        left, right = st.columns(2)

        with left:

            st.write(
                f"**Document Type:** "
                f"{document.document_type}"
            )

            st.write(
                f"**Vendor:** "
                f"{document.vendor_name or 'N/A'}"
            )

            st.write(
                f"**Invoice Number:** "
                f"{document.invoice_number or 'N/A'}"
            )

            st.write(
                f"**Invoice Date:** "
                f"{document.invoice_date or 'N/A'}"
            )

        with right:

            st.write(
                f"**Currency:** "
                f"{document.currency}"
            )

            st.write(
                f"**Subtotal:** "
                f"{document.subtotal or 'N/A'}"
            )

            st.write(
                f"**Tax:** "
                f"{document.tax_amount or 'N/A'}"
            )

            st.write(
                f"**Total:** "
                f"{document.total_amount or 'N/A'}"
            )

            st.write(
                f"**Payment Terms:** "
                f"{document.payment_terms or 'N/A'}"
            )


    # ========================================================
    # LINE ITEMS
    # ========================================================

    st.header("🛒 Line Items")

    if document.line_items:

        rows = []

        for item in document.line_items:

            rows.append(
                {
                    "Description": item.description,
                    "Quantity": item.quantity,
                    "Unit Price": item.unit_price,
                    "Total Price": item.total_price,
                    "Category": (
                        item.category
                        or "N/A"
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No line items were extracted."
        )


    # ========================================================
    # FINANCIAL AUDIT
    # ========================================================

    st.divider()

    st.header("🔍 Financial Audit")


    # ========================================================
    # RISK SUMMARY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Risk Score",
            f"{audit.risk_score:.0f}/100",
        )

    with col2:

        st.metric(
            "Risk Level",
            audit.risk_level,
        )

    with col3:

        st.metric(
            "Checks Performed",
            audit.checks_performed,
        )

    with col4:

        st.metric(
            "Checks Failed",
            audit.checks_failed,
        )


    # ========================================================
    # AUDIT SUMMARY
    # ========================================================

    st.subheader("📊 Audit Summary")

    if audit.risk_level == "HIGH":

        st.error(
            audit.summary
        )

    elif audit.risk_level == "MEDIUM":

        st.warning(
            audit.summary
        )

    else:

        st.success(
            audit.summary
        )


    # ========================================================
    # CHECK STATUS
    # ========================================================

    st.subheader("✅ Financial Checks")

    check_col1, check_col2 = st.columns(2)

    with check_col1:

        st.metric(
            "Checks Passed",
            audit.checks_passed,
        )

    with check_col2:

        st.metric(
            "Checks Failed",
            audit.checks_failed,
        )


    # ========================================================
    # AUDIT FINDINGS
    # ========================================================

    st.subheader("⚠️ Audit Findings")

    if not audit.findings:

        st.success(
            "✅ No financial inconsistencies "
            "were detected."
        )

    else:

        for index, finding in enumerate(
            audit.findings,
            start=1,
        ):

            severity = (
                finding.severity.upper()
            )

            # --------------------------------------------
            # HIGH
            # --------------------------------------------

            if severity == "HIGH":

                with st.container(
                    border=True
                ):

                    st.error(
                        f"🔴 Finding {index}: "
                        f"{finding.title}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{finding.category}"
                    )

                    st.write(
                        f"**Severity:** "
                        f"{finding.severity}"
                    )

                    st.write(
                        finding.message
                    )

                    if (
                        finding.expected_value
                        is not None
                    ):

                        st.write(
                            f"**Expected:** "
                            f"{finding.expected_value}"
                        )

                    if (
                        finding.actual_value
                        is not None
                    ):

                        st.write(
                            f"**Actual:** "
                            f"{finding.actual_value}"
                        )

                    if (
                        finding.difference
                        is not None
                    ):

                        st.write(
                            f"**Difference:** "
                            f"{finding.difference}"
                        )

            # --------------------------------------------
            # MEDIUM
            # --------------------------------------------

            elif severity == "MEDIUM":

                with st.container(
                    border=True
                ):

                    st.warning(
                        f"🟠 Finding {index}: "
                        f"{finding.title}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{finding.category}"
                    )

                    st.write(
                        finding.message
                    )

                    if (
                        finding.expected_value
                        is not None
                    ):

                        st.write(
                            f"**Expected:** "
                            f"{finding.expected_value}"
                        )

                    if (
                        finding.actual_value
                        is not None
                    ):

                        st.write(
                            f"**Actual:** "
                            f"{finding.actual_value}"
                        )

                    if (
                        finding.difference
                        is not None
                    ):

                        st.write(
                            f"**Difference:** "
                            f"{finding.difference}"
                        )

            # --------------------------------------------
            # LOW / OTHER
            # --------------------------------------------

            else:

                with st.container(
                    border=True
                ):

                    st.info(
                        f"🔵 Finding {index}: "
                        f"{finding.title}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{finding.category}"
                    )

                    st.write(
                        finding.message
                    )


    # ========================================================
    # FINANCIAL RECONCILIATION
    # ========================================================

    st.divider()

    st.header(
        "🧮 Financial Reconciliation"
    )

    if (
        document.subtotal is not None
        and document.tax_amount is not None
        and document.total_amount is not None
    ):

        expected_total = (
            document.subtotal
            + document.tax_amount
        )

        difference = (
            document.total_amount
            - expected_total
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            st.metric(
                "Subtotal + Tax",
                f"{document.currency} "
                f"{expected_total}",
            )

        with r2:

            st.metric(
                "Reported Total",
                f"{document.currency} "
                f"{document.total_amount}",
            )

        with r3:

            st.metric(
                "Difference",
                f"{document.currency} "
                f"{difference}",
            )

        if difference == 0:

            st.success(
                "✅ Subtotal + tax matches "
                "the reported total."
            )

        else:

            st.error(
                f"🚨 Total mismatch detected: "
                f"{document.currency} "
                f"{abs(difference)}"
            )

    else:

        st.info(
            "Insufficient financial values "
            "for total reconciliation."
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

    st.caption(
        "Financial AI Auditor • "
        "Extraction + Deterministic Financial Audit"
    )