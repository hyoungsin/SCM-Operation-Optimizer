import { getOutputFileUrl } from "../../api/resultApi";
import { getValidationReportUrl } from "../../api/validationApi";

export function ReportPanel({ state, resultReady }) {
  return (
    <section className="panel">
      <h2>Report</h2>
      <p>리포트 다운로드 단계입니다. Validation 이슈 리포트와 결과 Output 파일을 내려받을 수 있습니다.</p>
      <div className="actions">
        {state.validation && (
          <a className="button secondary" href={getValidationReportUrl(state.runId)}>
            Validation Report 다운로드
          </a>
        )}
        {resultReady && (
          <a className="button" href={getOutputFileUrl(state.runId)}>
            Output Excel 다운로드
          </a>
        )}
      </div>
    </section>
  );
}
