from __future__ import annotations

from models import MetadataReport, SteganographyReport


def format_metadata_report(report: MetadataReport) -> str:
    # Render metadata results as a plain-text report.
    lines = [
        f"File: {report.file_path}",
        f"Lat/Lon: {report.latitude if report.latitude is not None else 'N/A'} / {report.longitude if report.longitude is not None else 'N/A'}",
        f"Device: {_device_label(report)}",
        f"Software: {report.software or 'N/A'}",
        f"Date: {report.captured_at or 'N/A'}",
    ]
    return "\n".join(lines)


def _device_label(report: MetadataReport) -> str:
    # Merge make and model into a single display label.
    parts = [part for part in [report.device_make, report.device_model] if part]
    return " ".join(parts) if parts else "N/A"


def format_steganography_report(report: SteganographyReport) -> str:
    # Render a detection result or a fallback message when nothing is recovered.
    if not report.hidden_text:
        return "\n".join(
            [
                f"File: {report.file_path}",
                "Hidden Data: No supported hidden text detected in LSB stream.",
            ]
        )

    return "\n".join(
        [
            f"File: {report.file_path}",
            f"Detected Format: {report.detected_format or 'Unknown'}",
            report.hidden_text,
        ]
    )
