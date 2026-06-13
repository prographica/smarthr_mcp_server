import os
import json
import logging
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict, Any

from smarthr_mcp_server.auth import build_google_auth, DomainRestrictionMiddleware
from smarthr_mcp_server.smarthr_client import (
    SmartHRClient,
    CrewCreateRequest,
    CrewUpdateRequest,
    DepartmentCreateRequest,
    DepartmentUpdateRequest,
    DepartmentPartialUpdateRequest,
    DepartmentDiscontinueRequest,
    EmploymentTypeCreateRequest,
    EmploymentTypeUpdateRequest,
    EmploymentTypePartialUpdateRequest,
    JobTitleCreateRequest,
    JobTitleUpdateRequest,
    JobTitlePartialUpdateRequest,
    GradeCreateRequest,
    GradeUpdateRequest,
    GradePartialUpdateRequest,
    JobCategoryCreateRequest,
    JobCategoryUpdateRequest,
    JobCategoryPartialUpdateRequest,
    DependentCreateRequest,
    DependentPartialUpdateRequest
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smarthr-mcp-server")

smarthr_client = SmartHRClient()

# Google OAuth (claude.ai リモートコネクタ向け)。DISABLE_AUTH=1 で無効化可。
_auth_provider = build_google_auth()
mcp = FastMCP("SmartHR", auth=_auth_provider)
# 認証済みユーザーを社内ドメインに限定
mcp.add_middleware(DomainRestrictionMiddleware())

# --------------------
# TOOL: create_crew
# --------------------
@mcp.tool()
def smarthr_create_crew(data: dict) -> dict:
    """
    指定したIDの従業員情報を登録します。

    Args:
        登録する従業員のID
    """
    crew_data = CrewCreateRequest(**data)
    return smarthr_client.create_crew(crew_data)

# --------------------
# TOOL: get_crew
# --------------------
@mcp.tool()
def smarthr_get_crew(crew_id: str) -> dict:
    """
    指定したIDの従業員情報を取得します。

    Args:
        情報を取得する従業員のID
    """
    return smarthr_client.get_crew(crew_id)

# --------------------
# TOOL: update_crew
# --------------------
@mcp.tool()
def smarthr_update_crew(crew_id: str, data: dict) -> dict:
    """
    指定したIDの従業員情報を更新します。

    Args:
        情報を更新する従業員のID
    """
    crew_data = CrewUpdateRequest(**data)
    return smarthr_client.update_crew(crew_id, crew_data)

# --------------------
# TOOL: list_crews
# --------------------
@mcp.tool()
def smarthr_list_crews(
    page: int = 1,
    per_page: int = 10,
    emp_code: Optional[str] = None,
    employment_type_id: Optional[str] = None,
    department_id: Optional[str] = None,
    entered_at_from: Optional[str] = None,
    entered_at_to: Optional[str] = None,
) -> dict:
    """
    従業員のリストを取得します。

    Args:
        page: ページ番号
        per_page: 1ページあたりの件数
        emp_code: 社員番号での絞り込み
        employment_type_id: 雇用形態IDでの絞り込み
        department_id: 部署IDでの絞り込み
        entered_at_from / entered_at_to: 入社日の範囲 (YYYY-MM-DD)
    """
    filters = {
        "emp_code": emp_code,
        "employment_type_id": employment_type_id,
        "department_id": department_id,
        "entered_at_from": entered_at_from,
        "entered_at_to": entered_at_to,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    return smarthr_client.list_crews(page=page, per_page=per_page, **filters)

# --------------------
# TOOL: search_crews
# --------------------
@mcp.tool()
def smarthr_search_crews(query: str, page: int = 1, per_page: int = 10) -> dict:
    """
    従業員を検索します。
    """
    return smarthr_client.search_crews(query=query, page=page, per_page=per_page)

# --------------------
# TOOL: delete_crew
# --------------------
@mcp.tool()
def smarthr_delete_crew(crew_id: str) -> None:
    """
    指定したIDの従業員情報を削除します。

    Args:
        削除する従業員のID
    """
    smarthr_client.delete_crew(crew_id)

# --------------------
# TOOL: invite_crew
# --------------------
@mcp.tool()
def smarthr_invite_crew(crew_id: str, inviter_user_id: Optional[str] = None, crew_input_form_id: Optional[str] = None) -> Dict[str, Any]:
    """
    指定した従業員に設定されているメールアドレスでユーザーを招待します。

    Args:
        crew_id (str): 招待する従業員のID
        inviter_user_id (Optional[str], optional): 招待者のユーザーID
        crew_input_form_id (Optional[str], optional): 従業員情報収集フォームのID

    Returns:
        Dict[str, Any]: 招待APIのレスポンス
    """
    return smarthr_client.invite_crew(crew_id, inviter_user_id, crew_input_form_id)

# --------------------
# TOOL: create_department
# --------------------
@mcp.tool()
def smarthr_create_department(name: str, position: Optional[int] = None, code: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    新しい部署を作成します。

    Args:
        name (str): 部署名
        position (Optional[int], optional): 部署の位置
        code (Optional[str], optional): 部署コード
        parent_id (Optional[str], optional): 親部署のID

    Returns:
        Dict[str, Any]: 作成された部署の情報
    """
    department_data = DepartmentCreateRequest(
        name=name,
        position=position,
        code=code,
        parent_id=parent_id
    )
    return smarthr_client.create_department(department_data)

# --------------------
# TOOL: list_departments
# --------------------
@mcp.tool()
def smarthr_list_departments(page: int = 1, per_page: int = 10, code: Optional[str] = None, sort: Optional[str] = None) -> Dict[str, Any]:
    """
    部署のリストを取得します。

    Args:
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.
        code (Optional[str], optional): 部署コード. Defaults to None.
        sort (Optional[str], optional): 並び順. Defaults to None.

    Returns:
        Dict[str, Any]: 部署のリスト情報
    """
    return smarthr_client.list_departments(page=page, per_page=per_page, code=code, sort=sort)

# --------------------
# TOOL: get_department
# --------------------
@mcp.tool()
def smarthr_get_department(department_id: str) -> Dict[str, Any]:
    """
    指定したIDの部署情報を取得します。

    Args:
        department_id (str): 取得する部署のID

    Returns:
        Dict[str, Any]: 部署情報
    """
    return smarthr_client.get_department(department_id)

# --------------------
# TOOL: update_department
# --------------------
@mcp.tool()
def smarthr_update_department(department_id: str, name: str, position: Optional[int] = None, code: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    指定したIDの部署情報を更新します。

    Args:
        department_id (str): 更新する部署のID
        name (str): 部署名
        position (Optional[int], optional): 部署の位置
        code (Optional[str], optional): 部署コード
        parent_id (Optional[str], optional): 親部署のID

    Returns:
        Dict[str, Any]: 更新された部署の情報
    """
    department_data = DepartmentUpdateRequest(
        name=name,
        position=position,
        code=code,
        parent_id=parent_id
    )
    return smarthr_client.update_department(department_id, department_data)

# --------------------
# TOOL: partial_update_department
# --------------------
@mcp.tool()
def smarthr_partial_update_department(department_id: str, name: Optional[str] = None, position: Optional[int] = None, code: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    指定したIDの部署情報を部分更新します。

    Args:
        department_id (str): 更新する部署のID
        name (Optional[str], optional): 部署名
        position (Optional[int], optional): 部署の位置
        code (Optional[str], optional): 部署コード
        parent_id (Optional[str], optional): 親部署のID

    Returns:
        Dict[str, Any]: 更新された部署の情報
    """
    department_data = DepartmentPartialUpdateRequest(
        name=name,
        position=position,
        code=code,
        parent_id=parent_id
    )
    return smarthr_client.partial_update_department(department_id, department_data)

# --------------------
# TOOL: discontinue_department
# --------------------
@mcp.tool()
def smarthr_discontinue_department(department_id: str, discontinued_date: str) -> Dict[str, Any]:
    """
    指定したIDの部署を廃止します。

    Args:
        department_id (str): 廃止する部署のID
        discontinued_date (str): 部署が存続していた最後の日付 (YYYY-MM-DD形式)

    Returns:
        Dict[str, Any]: 廃止された部署の情報
    """
    return smarthr_client.discontinue_department(department_id, discontinued_date)

# --------------------
# TOOL: list_employment_types
# --------------------
@mcp.tool()
def smarthr_list_employment_types(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    雇用形態のリストを取得します。

    Args:
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.

    Returns:
        Dict[str, Any]: 雇用形態のリスト情報
    """
    return smarthr_client.list_employment_types(page=page, per_page=per_page)

# --------------------
# TOOL: create_employment_type
# --------------------
@mcp.tool()
def smarthr_create_employment_type(name: str, code: Optional[str] = None) -> Dict[str, Any]:
    """
    新しい雇用形態を作成します。

    Args:
        name (str): 雇用形態の名称
        code (Optional[str], optional): 雇用形態のコード

    Returns:
        Dict[str, Any]: 作成された雇用形態の情報
    """
    employment_type_data = EmploymentTypeCreateRequest(
        name=name,
        code=code
    )
    return smarthr_client.create_employment_type(employment_type_data)

# --------------------
# TOOL: get_employment_type
# --------------------
@mcp.tool()
def smarthr_get_employment_type(employment_type_id: str) -> Dict[str, Any]:
    """
    指定したIDの雇用形態情報を取得します。

    Args:
        employment_type_id (str): 取得する雇用形態のID

    Returns:
        Dict[str, Any]: 雇用形態情報
    """
    return smarthr_client.get_employment_type(employment_type_id)

# --------------------
# TOOL: update_employment_type
# --------------------
@mcp.tool()
def smarthr_update_employment_type(employment_type_id: str, name: str) -> Dict[str, Any]:
    """
    指定したIDの雇用形態情報を更新します。

    Args:
        employment_type_id (str): 更新する雇用形態のID
        name (str): 雇用形態の新しい名称

    Returns:
        Dict[str, Any]: 更新された雇用形態の情報
    """
    employment_type_data = EmploymentTypeUpdateRequest(name=name)
    return smarthr_client.update_employment_type(employment_type_id, employment_type_data)

# --------------------
# TOOL: partial_update_employment_type
# --------------------
@mcp.tool()
def smarthr_partial_update_employment_type(employment_type_id: str, name: Optional[str] = None, code: Optional[str] = None) -> Dict[str, Any]:
    """
    指定したIDの雇用形態情報を部分更新します。

    Args:
        employment_type_id (str): 更新する雇用形態のID
        name (Optional[str], optional): 雇用形態の新しい名称
        code (Optional[str], optional): 雇用形態の新しいコード

    Returns:
        Dict[str, Any]: 更新された雇用形態の情報
    """
    employment_type_data = EmploymentTypePartialUpdateRequest(
        name=name,
        code=code
    )
    return smarthr_client.partial_update_employment_type(employment_type_id, employment_type_data)

# --------------------
# TOOL: delete_employment_type
# --------------------
@mcp.tool()
def smarthr_delete_employment_type(employment_type_id: str) -> None:
    """
    指定したIDの雇用形態情報を削除します。

    Args:
        employment_type_id (str): 削除する雇用形態のID
    """
    smarthr_client.delete_employment_type(employment_type_id)

# --------------------
# TOOL: list_job_titles
# --------------------
@mcp.tool()
def smarthr_list_job_titles(page: int = 1, per_page: int = 10, sort: Optional[str] = None) -> Dict[str, Any]:
    """
    役職情報のリストを取得します。

    Args:
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.
        sort (Optional[str], optional): 並び順. Defaults to None.

    Returns:
        Dict[str, Any]: 役職情報のリスト
    """
    return smarthr_client.list_job_titles(page=page, per_page=per_page, sort=sort)

# --------------------
# TOOL: create_job_title
# --------------------
@mcp.tool()
def smarthr_create_job_title(name: str, rank: int, code: Optional[str] = None) -> Dict[str, Any]:
    """
    新しい役職情報を作成します。

    Args:
        name (str): 役職の名前
        rank (int): 役職のランク
        code (Optional[str], optional): 役職コード

    Returns:
        Dict[str, Any]: 作成された役職情報
    """
    job_title_data = JobTitleCreateRequest(
        name=name,
        rank=rank,
        code=code
    )
    return smarthr_client.create_job_title(job_title_data)

# --------------------
# TOOL: get_job_title
# --------------------
@mcp.tool()
def smarthr_get_job_title(job_title_id: str) -> Dict[str, Any]:
    """
    指定したIDの役職情報を取得します。

    Args:
        job_title_id (str): 取得する役職のID

    Returns:
        Dict[str, Any]: 役職情報
    """
    return smarthr_client.get_job_title(job_title_id)

# --------------------
# TOOL: update_job_title
# --------------------
@mcp.tool()
def smarthr_update_job_title(job_title_id: str, name: str, rank: int) -> Dict[str, Any]:
    """
    指定したIDの役職情報を更新します。

    Args:
        job_title_id (str): 更新する役職のID
        name (str): 役職の新しい名前
        rank (int): 役職の新しいランク

    Returns:
        Dict[str, Any]: 更新された役職情報
    """
    job_title_data = JobTitleUpdateRequest(
        name=name,
        rank=rank
    )
    return smarthr_client.update_job_title(job_title_id, job_title_data)

# --------------------
# TOOL: partial_update_job_title
# --------------------
@mcp.tool()
def smarthr_partial_update_job_title(job_title_id: str, name: Optional[str] = None, rank: Optional[int] = None, code: Optional[str] = None) -> Dict[str, Any]:
    """
    指定したIDの役職情報を部分更新します。

    Args:
        job_title_id (str): 更新する役職のID
        name (Optional[str], optional): 役職の新しい名前
        rank (Optional[int], optional): 役職の新しいランク
        code (Optional[str], optional): 役職の新しいコード

    Returns:
        Dict[str, Any]: 更新された役職情報
    """
    job_title_data = JobTitlePartialUpdateRequest(
        name=name,
        rank=rank,
        code=code
    )
    return smarthr_client.partial_update_job_title(job_title_id, job_title_data)

# --------------------
# TOOL: delete_job_title
# --------------------
@mcp.tool()
def smarthr_delete_job_title(job_title_id: str) -> None:
    """
    指定したIDの役職情報を削除します。

    Args:
        job_title_id (str): 削除する役職のID
    """
    smarthr_client.delete_job_title(job_title_id)

# --------------------
# TOOL: list_grades
# --------------------
@mcp.tool()
def smarthr_list_grades(page: int = 1, per_page: int = 10, sort: Optional[str] = None) -> Dict[str, Any]:
    """
    等級のリストを取得します。

    Args:
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.
        sort (Optional[str], optional): 並び順. Defaults to None.

    Returns:
        Dict[str, Any]: 等級のリスト情報
    """
    return smarthr_client.list_grades(page=page, per_page=per_page, sort=sort)

# --------------------
# TOOL: create_grade
# --------------------
@mcp.tool()
def smarthr_create_grade(name: str, rank: int) -> Dict[str, Any]:
    """
    新しい等級を作成します。

    Args:
        name (str): 等級の名前
        rank (int): 等級のランク

    Returns:
        Dict[str, Any]: 作成された等級の情報
    """
    grade_data = GradeCreateRequest(name=name, rank=rank)
    return smarthr_client.create_grade(grade_data)

# --------------------
# TOOL: get_grade
# --------------------
@mcp.tool()
def smarthr_get_grade(grade_id: str) -> Dict[str, Any]:
    """
    指定したIDの等級情報を取得します。

    Args:
        grade_id (str): 取得する等級のID

    Returns:
        Dict[str, Any]: 等級情報
    """
    return smarthr_client.get_grade(grade_id)

# --------------------
# TOOL: update_grade
# --------------------
@mcp.tool()
def smarthr_update_grade(grade_id: str, name: str, rank: int) -> Dict[str, Any]:
    """
    指定したIDの等級情報を更新します。

    Args:
        grade_id (str): 更新する等級のID
        name (str): 等級の新しい名前
        rank (int): 等級の新しいランク

    Returns:
        Dict[str, Any]: 更新された等級の情報
    """
    grade_data = GradeUpdateRequest(name=name, rank=rank)
    return smarthr_client.update_grade(grade_id, grade_data)

# --------------------
# TOOL: partial_update_grade
# --------------------
@mcp.tool()
def smarthr_partial_update_grade(grade_id: str, name: Optional[str] = None, rank: Optional[int] = None) -> Dict[str, Any]:
    """
    指定したIDの等級情報を部分更新します。

    Args:
        grade_id (str): 更新する等級のID
        name (Optional[str], optional): 等級の新しい名前
        rank (Optional[int], optional): 等級の新しいランク

    Returns:
        Dict[str, Any]: 更新された等級の情報
    """
    grade_data = GradePartialUpdateRequest(name=name, rank=rank)
    return smarthr_client.partial_update_grade(grade_id, grade_data)

# --------------------
# TOOL: delete_grade
# --------------------
@mcp.tool()
def smarthr_delete_grade(grade_id: str) -> None:
    """
    指定したIDの等級情報を削除します。

    Args:
        grade_id (str): 削除する等級のID
    """
    smarthr_client.delete_grade(grade_id)

# --------------------
# TOOL: list_job_categories
# --------------------
@mcp.tool()
def smarthr_list_job_categories(page: int = 1, per_page: int = 10, sort: Optional[str] = None) -> Dict[str, Any]:
    """
    職種のリストを取得します。

    Args:
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.
        sort (Optional[str], optional): 並び順. Defaults to None.

    Returns:
        Dict[str, Any]: 職種のリスト情報
    """
    return smarthr_client.list_job_categories(page=page, per_page=per_page, sort=sort)

# --------------------
# TOOL: create_job_category
# --------------------
@mcp.tool()
def smarthr_create_job_category(name: str) -> Dict[str, Any]:
    """
    新しい職種を作成します。

    Args:
        name (str): 職種の名前

    Returns:
        Dict[str, Any]: 作成された職種の情報
    """
    job_category_data = JobCategoryCreateRequest(name=name)
    return smarthr_client.create_job_category(job_category_data)

# --------------------
# TOOL: get_job_category
# --------------------
@mcp.tool()
def smarthr_get_job_category(job_category_id: str) -> Dict[str, Any]:
    """
    指定したIDの職種情報を取得します。

    Args:
        job_category_id (str): 取得する職種のID

    Returns:
        Dict[str, Any]: 職種情報
    """
    return smarthr_client.get_job_category(job_category_id)

# --------------------
# TOOL: update_job_category
# --------------------
@mcp.tool()
def smarthr_update_job_category(job_category_id: str, name: str) -> Dict[str, Any]:
    """
    指定したIDの職種情報を更新します。

    Args:
        job_category_id (str): 更新する職種のID
        name (str): 職種の新しい名前

    Returns:
        Dict[str, Any]: 更新された職種の情報
    """
    job_category_data = JobCategoryUpdateRequest(name=name)
    return smarthr_client.update_job_category(job_category_id, job_category_data)

# --------------------
# TOOL: partial_update_job_category
# --------------------
@mcp.tool()
def smarthr_partial_update_job_category(job_category_id: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    指定したIDの職種情報を部分更新します。

    Args:
        job_category_id (str): 更新する職種のID
        name (Optional[str], optional): 職種の新しい名前

    Returns:
        Dict[str, Any]: 更新された職種の情報
    """
    job_category_data = JobCategoryPartialUpdateRequest(name=name)
    return smarthr_client.partial_update_job_category(job_category_id, job_category_data)

# --------------------
# TOOL: delete_job_category
# --------------------
@mcp.tool()
def smarthr_delete_job_category(job_category_id: str) -> None:
    """
    指定したIDの職種情報を削除します。

    Args:
        job_category_id (str): 削除する職種のID
    """
    smarthr_client.delete_job_category(job_category_id)

# --------------------
# TOOL: list_dependents
# --------------------
@mcp.tool()
def smarthr_list_dependents(crew_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    指定した従業員の家族情報のリストを取得します。

    Args:
        crew_id (str): 従業員ID
        page (int, optional): 取得するページ番号. Defaults to 1.
        per_page (int, optional): 1ページあたりの結果数. Defaults to 10.

    Returns:
        Dict[str, Any]: 家族情報のリスト
    """
    return smarthr_client.list_dependents(crew_id, page=page, per_page=per_page)

# --------------------
# TOOL: create_dependent
# --------------------
@mcp.tool()
def smarthr_create_dependent(crew_id: str, dependent_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    指定した従業員の家族情報を新規作成します。

    Args:
        crew_id (str): 従業員ID
        dependent_data (dict): 作成する家族情報

    Returns:
        Dict[str, Any]: 作成された家族情報
    """
    try:
        model = DependentCreateRequest(**dependent_data)
        client = SmartHRClient()
        return client.create_dependent(crew_id=crew_id, dependent_data=model)
    except ValidationError as e:
        # Pydanticのバリデーションエラーを明示的に返す
        return {
            "error": "入力内容に誤りがあります。",
            "details": e.errors()
        }
    except Exception as e:
        return {
            "error": "依存情報の登録中に予期せぬエラーが発生しました。",
            "details": str(e)
        }


# --------------------
# TOOL: get_dependent
# --------------------
@mcp.tool()
def smarthr_get_dependent(crew_id: str, dependent_id: str) -> Dict[str, Any]:
    """
    指定した従業員の特定の家族情報を取得します。

    Args:
        crew_id (str): 従業員ID
        dependent_id (str): 家族情報ID

    Returns:
        Dict[str, Any]: 家族情報
    """
    return smarthr_client.get_dependent(crew_id, dependent_id)

# --------------------
# TOOL: update_dependent
# --------------------
@mcp.tool()
def smarthr_update_dependent(crew_id: str, dependent_id: str, dependent_data: dict) -> Dict[str, Any]:
    """
    指定した従業員の家族情報を更新します。

    Args:
        crew_id (str): 従業員ID
        dependent_id (str): 家族情報ID
        dependent_data (dict): 更新する家族情報

    Returns:
        Dict[str, Any]: 更新された家族情報
    """
    dependent_request = DependentUpdateRequest(**dependent_data)
    return smarthr_client.update_dependent(crew_id, dependent_id, dependent_request)

# --------------------
# TOOL: partial_update_dependent
# --------------------
@mcp.tool()
def smarthr_partial_update_dependent(crew_id: str, dependent_id: str, dependent_data: dict) -> Dict[str, Any]:
    """
    指定した従業員の家族情報を部分更新します。

    Args:
        crew_id (str): 従業員ID
        dependent_id (str): 家族情報ID
        dependent_data (dict): 部分更新する家族情報

    Returns:
        Dict[str, Any]: 更新された家族情報
    """
    dependent_request = DependentPartialUpdateRequest(**dependent_data)
    return smarthr_client.partial_update_dependent(crew_id, dependent_id, dependent_request)

# --------------------
# TOOL: delete_dependent
# --------------------
@mcp.tool()
def smarthr_delete_dependent(crew_id: str, dependent_id: str) -> None:
    """
    指定した従業員の家族情報を削除します。

    Args:
        crew_id (str): 従業員ID
        dependent_id (str): 家族情報ID
    """
    smarthr_client.delete_dependent(crew_id, dependent_id)

# --------------------
# TOOL: list_relations
# --------------------
@mcp.tool()
def smarthr_list_relations(page: int = 1, per_page: int = 100) -> Dict[str, Any]:
    """
    SmartHRの続柄（relation）一覧を取得する関数（MCPツール向け）

    Args:
        page (int): ページ番号
        per_page (int): 1ページあたりの件数

    Returns:
        Dict[str, Any]: APIレスポンス（続柄リスト）
    """
    client = SmartHRClient()
    result = client.list_relations(page=page, per_page=per_page)
    return result

# --------------------
# RESOURCE: smarthr://crew_profiles
# --------------------
@mcp.resource("smarthr://crew_profiles")
def smarthr_read_crew_profiles() -> dict:
    crews = smarthr_client.list_crews(per_page=5)
    return {
        "crew_profiles": {
            "total_crews": crews.get('total', 0),
            "page_info": crews.get('page_info', {}),
            "sample_crews": crews.get('data', [])
        }
    }