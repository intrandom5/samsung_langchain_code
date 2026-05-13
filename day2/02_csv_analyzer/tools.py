import io
import base64
import contextlib

import matplotlib
matplotlib.use("Agg")  # Streamlit에서는 non-interactive 백엔드 필요
import matplotlib.pyplot as plt
import pandas as pd
from langchain.tools import tool

# 현재 업로드된 DataFrame (app.py에서 set_dataframe()으로 설정)
_df = None
_figure_b64 = None


def set_dataframe(df: pd.DataFrame):
    """CSV 업로드 후 DataFrame을 도구에 전달합니다."""
    global _df
    _df = df


def get_figure():
    """마지막으로 생성된 matplotlib 차트를 base64로 반환합니다."""
    global _figure_b64
    result, _figure_b64 = _figure_b64, None  # 반환 후 초기화
    return result


@tool
def run_python(code: str) -> str:
    """
    pandas(df)와 matplotlib(plt)으로 데이터 분석 코드를 실행합니다.

    사용 가능한 변수:
    - df  : 업로드된 CSV 데이터 (pandas DataFrame)
    - pd  : pandas 라이브러리
    - plt : matplotlib.pyplot

    규칙:
    - 수치 결과는 print()로 출력하세요.
    - 차트는 plt.show()를 호출하면 자동 저장됩니다.
    """
    global _figure_b64

    if _df is None:
        return "데이터가 로드되지 않았습니다."

    stdout_buf = io.StringIO()
    namespace = {"df": _df, "pd": pd, "plt": plt}

    try:
        with contextlib.redirect_stdout(stdout_buf):
            exec(code, namespace)  # noqa: S102

        text = stdout_buf.getvalue()

        # matplotlib 차트가 생성되었으면 base64로 변환해서 저장
        if plt.get_fignums():
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
            buf.seek(0)
            _figure_b64 = base64.b64encode(buf.read()).decode()
            plt.close("all")
            text += "\n[차트가 생성되었습니다]"

        return text.strip() or "코드 실행 완료 (출력 없음)"

    except Exception as e:
        return f"오류 ({type(e).__name__}): {e}"
