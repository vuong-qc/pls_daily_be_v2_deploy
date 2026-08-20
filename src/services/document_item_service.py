from typing import Optional
import asyncio
from src.models.document_result.request.filter_document_result_model import FilterDocumentResult
from src.enums.bug_status_enum import BugStatusEnum
from src.enums.document_result_evaluate import DocumentResultEvaluate
from src.models.group.response.group_reponse_model import GroupSummaryResponseModel
from src.models.group.request.filter_group_model import FilterGroupModel
from src.models.work_item.request.filter_work_item import FilterWorkItemModel
from src.exception.project_exception import ProjectException, ProjectMessage, ProjectStatusCode
from src.models.response_model import ResponseModel, ResponsePaginatedModel
from src.repositories.document_item.beanie_document_item_repository import DocumentItemRepository
from src.models.document_item.request.filter_document_item_model import FilterDocumentItem
from src.models.document_item.request.update_document_item_model import UpdateDocumentItem
from src.models.document_item.request.create_document_item_model import CreateDocumentItem
from src.models.document_item.response.document_item_response_model import DocumentResponse
from src.exception.document_exception import DocumentException, DocumentMessage, DocumentStatusCode
from src.repositories.work_item.work_item_repository import WorkItemRepository
from src.models.document_result.response.document_result_response import DocumentResultResponse
from src.repositories.document_result.document_result_repository import DocumentResultRepository
# from src.exception.sprint_exception import SprintException, SprintMessage, SprintStatusCode
from src.enums.work_item_type import DocumentParentType, WorkItemType
from src.models.document_result.request.create_document_result_model import CreateDocumentResult
from src.models.document_result.request.update_document_result_model import UpdateDocumentResult
# from src.models.document_result.request.filter_document_result_model import FilterDocumentResult
from src.enums.user_role_enum import UserRole
from src.enums.group_type_enum import GroupType
from src.repositories.group.group_repository import GroupRepository


from src.enums.document_type_enum import DocumentTypeEnum

class DocumentItemService:
    def __init__(self, repository: DocumentItemRepository, work_item_repository: WorkItemRepository,
                 document_result_repository: DocumentResultRepository, group_repository: GroupRepository):
        self.repository = repository
        self.work_item_repository = work_item_repository
        self.document_result_repository = document_result_repository
        self.group_repository = group_repository

    async def create_document(self, data: CreateDocumentItem, roles: Optional[list]=None, user_id: Optional[str] = None) -> ResponseModel:
        if data.type == DocumentTypeEnum.TODO and data.ftf:
            # check first thing first, count todo
            # if count = 5 raise error
            filter_todo = FilterDocumentItem(type=[DocumentTypeEnum.TODO], offset=0, limit=1, object_id=[data.object_id], ftf=True, is_checked=False)
            list_doc, total = await self.repository.get_list_document_items(filter_todo)
            if total>= 5:
                raise DocumentException(DocumentMessage.CANT_ASSIGN_FTF, DocumentStatusCode.CANT_ASSIGN_FTF)

        #write func check for group
        # check role for type
        data.created_by = user_id
        # if data.parent_type and data.object_id:
        #     await self._check_role_with_doc_type(data.type, roles, data.created_by,data.object_id, data.parent_type)
        document = await self.repository.create_document(data.model_dump())
        response = DocumentResponse.model_validate(document)
        # auto create doc result
        create_result_data = CreateDocumentResult(parent_id = str(response.id), owner_id=user_id)
        result = await self.document_result_repository.create_document_result(create_result_data.model_dump())
        response.result = DocumentResultResponse.model_validate(result)
        return ResponseModel(data=response)

    async def update_document(self, document_id:str, data: UpdateDocumentItem, user_id:str, roles: Optional[list[int]] = None,) -> ResponseModel:
        old_document = await self.repository.get_document_item(document_id)
        if not old_document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        if old_document.type == DocumentTypeEnum.TODO and data.ftf:
            # check first thing first, count todo
            # if count = 5 raise error
            filter_todo = FilterDocumentItem(type=[DocumentTypeEnum.TODO], offset=0, limit=1, object_id=[old_document.object_id], ftf=True, is_checked=False)
            list_doc, total = await self.repository.get_list_document_items(filter_todo)
            if total>= 5:
                raise DocumentException(DocumentMessage.CANT_ASSIGN_FTF, DocumentStatusCode.CANT_ASSIGN_FTF)

        document = await self.repository.update_document(document_id, data)
        if not document:
             raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        # if document.parent_type:
        #     await self._check_role_with_doc_type(document.type, roles, user_id,document.object_id, document.parent_type)

        response = DocumentResponse.model_validate(document)
        return ResponseModel(data=response)

    async def update_document_result(self, user_id:str, document_result_id:str, data: UpdateDocumentResult) -> ResponseModel:
        doc_result = await self.document_result_repository.get_document_result(document_result_id)
        if not doc_result:
            raise DocumentException(DocumentMessage.DOCUMENT_RESULT_NOT_FOUND, DocumentStatusCode.DOCUMENT_RESULT_NOT_FOUND)
        # if doc_result.owner_id != user_id:
        #     raise DocumentException(DocumentMessage.NOT_CREATOR, DocumentStatusCode.NOT_CREATOR)
        # print("doc result", doc_result)
        updated_document = await self.document_result_repository.update_document_result(document_result_id, data.model_dump(exclude_unset=True))
        if not updated_document:
            raise DocumentException(DocumentMessage.DOCUMENT_RESULT_NOT_FOUND, DocumentStatusCode.DOCUMENT_RESULT_NOT_FOUND)
        return ResponseModel(data=DocumentResultResponse.model_validate(updated_document))

    async def delete_document(self, document_id:str, user_id: str):
        document = await self.repository.get_document_item(document_id)
        if not document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        if document.created_by and document.created_by != user_id:
            raise DocumentException(DocumentMessage.NOT_CREATOR, DocumentStatusCode.NOT_CREATOR)
        await self.repository.delete_document(document_id)
        return ResponseModel()

    async def get_document(self, document_id:str):
        document = await self.repository.get_document_item(document_id)
        if not document:
            raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
        response = DocumentResponse.model_validate(document)
        return ResponseModel(data=response)

    async def get_list_document(self, filters: FilterDocumentItem, user_id: str) -> ResponsePaginatedModel:
        list_document, total = await self.repository.get_list_document_items(filters)
        list_res = []
        for document in list_document:
            response = DocumentResponse.model_validate(document)
            # get result of doc
            result = await self.document_result_repository.get_document_result_by_parent_id(str(response.id),user_id)
            if not result:
                create_result_data = CreateDocumentResult(parent_id=str(response.id))
                create_result_data.owner_id = user_id
                result = await self.document_result_repository.create_document_result(create_result_data.model_dump())
            response.result = DocumentResultResponse.model_validate(result)
            list_res.append(response)
        return ResponsePaginatedModel(data=list_res, total=total, offset=filters.offset)

    async def _check_role_with_doc_type(self,doc_type:str, roles: list[int], user_id:str, object_id: Optional[str] = None, parent_type: Optional[str] = None):
        if object_id and user_id and parent_type:
            # check work_item exist and match type
            work_item = await self.work_item_repository.get_work_item_by_id(object_id)
            if not work_item:
                raise DocumentException(DocumentMessage.NOT_FOUND, DocumentStatusCode.NOT_FOUND)
            if work_item.type != parent_type:
                raise DocumentException(DocumentMessage.PARENT_TYPE_NOT_MATCH, DocumentStatusCode.PARENT_TYPE_NOT_MATCH)
            if doc_type == DocumentTypeEnum.QA:
                if UserRole.TASKER.value in roles:
                    if work_item.type != WorkItemType.SPRINT or parent_type != WorkItemType.SPRINT:
                        raise DocumentException(DocumentMessage.TASKER_NOT_MATCH_SPRINT, DocumentStatusCode.TASKER_NOT_MATCH_SPRINT)
                    # parent type is sprint
                    else:
                        if user_id not in work_item.assigned_id:
                            raise DocumentException(DocumentMessage.TASKER_NOT_MATCH_SPRINT, DocumentStatusCode.TASKER_NOT_MATCH_SPRINT)

                elif UserRole.HANDLER.value in roles:
                    if work_item.type == WorkItemType.SPRINT:
                        project = await self.work_item_repository.get_work_item_by_id(work_item.parent)
                        if not project:
                            raise ProjectException(ProjectMessage.NOT_FOUND, ProjectStatusCode.NOT_FOUND)
                        if user_id not in project.handler_id:
                            raise ProjectException(ProjectMessage.NOT_HANDLER_PROJECT, ProjectStatusCode.NOT_HANDLER_PROJECT)
                    elif work_item.type == WorkItemType.PROJECT:
                        if user_id not in work_item.handler_id:
                            raise ProjectException(ProjectMessage.NOT_HANDLER_PROJECT, ProjectStatusCode.NOT_HANDLER_PROJECT)
        else:
            raise DocumentException(DocumentMessage.NOT_ENOUGH_DATA, DocumentStatusCode.NOT_ENOUGH_DATA)

    async def statistic_todo(self, query: FilterDocumentItem):
        total_todo = await self.repository.count_items_by_time_buckets(query)
        query.is_checked = True
        todo_done_todo = await self.repository.count_completed_items_by_time_buckets(query)
        return ResponseModel(data={
            "total_todo": total_todo,
            "todo_done_todo": todo_done_todo
        })
    #
    async def count_checklist_doc_qa(self, project_id: str, user_id: str):
        """input : project_id
        output:
        - todo : list sub group and total sub group
        - bug: ... + verified bug
        - document: ...
        - tc: ... + pass tc
        """
        # DocumentTypeEnum.TODO # total, 1 1 layer
        # DocumentTypeEnum.QA # total and resolve
        # WorkItemType.BUG # total , 1 layer
        # DocumentTypeEnum.DOCUMENT # total => get group -> sub group count and return total
        # DocumentTypeEnum.TC # eva and to total

        filter_groups = FilterGroupModel(
            offset=0,
            limit=100,
            parent_ids=[project_id],
            type=[GroupType.TODO, GroupType.DOCUMENT, GroupType.TC, GroupType.BUG],
        )
        all_groups, _ = await self.group_repository.get_all_groups(filter_groups)

        groups_by_type: dict[str, list] = {}
        for g in all_groups:
            groups_by_type.setdefault(g.type, []).append(g)

        todo_groups = groups_by_type.get(GroupType.TODO, [])
        # print("todo_groups:", todo_groups)
        doc_groups = groups_by_type.get(GroupType.DOCUMENT, [])
        # print("doc_groups:", doc_groups)
        tc_groups = groups_by_type.get(GroupType.TC, [])
        # print("tc_groups:", tc_groups)
        bug_groups = groups_by_type.get(GroupType.BUG, [])
        # print("bug_groups:", bug_groups)

        # 2) Todo có 2 cấp -> query lần 2: lấy group con theo list id group cha vừa lấy
        doc_ids = [str(g.id) for g in doc_groups]
        filter_docs_child = filter_groups.model_copy(deep=True)
        filter_docs_child.parent_ids = doc_ids

        filter_todo_child = filter_groups.model_copy(deep=True)
        todo_ids = [str(g.id) for g in todo_groups]
        filter_todo_child.parent_ids = todo_ids
        filter_summary_tdo = FilterDocumentItem(offset=0, limit=1,object_id=[project_id],type=[DocumentTypeEnum.TODO], group_id=[None])
        # count
        (
            (docs_children, total),
            (todo_children, total_todo),
            (todo_summary_tdo, total_summary_todo),
        ) = await asyncio.gather(
            self.group_repository.get_all_groups(filter_docs_child),
            self.group_repository.get_all_groups(filter_todo_child),
            self.repository.get_all_document_items(filter_summary_tdo),
        )


        doc_all_ids = doc_ids + [str(c.id) for c in docs_children]
        todo_all_ids = todo_ids + [str(c.id) for c in todo_children]
        (
            doc_item_count_todo,
            doc_item_count_doc,
            bug_group_counts,
            bug_default_counts,
            tc_counts,
        ) = await asyncio.gather(
            self._count_document_items_by_group(todo_all_ids),
            self._count_document_items_by_group(doc_all_ids),
            self._count_bug_work_items_by_group([str(g.id) for g in bug_groups]),
            self._count_default_bug_work_items(project_id),
            self._count_tc_results_by_group([str(g.id) for g in tc_groups], user_id),
        )

        dict_group: dict[str, GroupSummaryResponseModel] = {}

        todo_result = self._build_doc(todo_groups, todo_children, doc_item_count_todo, dict_group)
        doc_result = self._build_doc(doc_groups, docs_children, doc_item_count_doc, dict_group)
        bug_result = self._build_bug(bug_groups, bug_group_counts, dict_group)
        tc_result = self._build_tc(tc_groups, tc_counts, dict_group)

        # format res
        default = []
        default.append(
            GroupSummaryResponseModel(
                type=GroupType.BUG,
                name="DEFAULT",
                total=bug_default_counts["total"],
                resolve=bug_default_counts["resolve"],
            )
        )
        summary_todo = []
        summary_todo.append(
            GroupSummaryResponseModel(
                type=GroupType.TODO,
                name="SUMMARY",
                total=total_summary_todo
            )
        )


        # count them checklist tong quan cua toi
        return ResponseModel(data={
            "todo": todo_result,
            "doc": doc_result,
            "bug": bug_result,
            "bug_default": default,
            "tc": tc_result,
            "summary": summary_todo,
        })
    @staticmethod
    def _to_node(g, counts: dict) -> GroupSummaryResponseModel:
        return GroupSummaryResponseModel(
            id=g.id,
            type=g.type,
            name=g.name,
            parent_id=g.parent_id,
            sub_type=g.sub_type,
            created_by=g.created_by,
            parent_type=g.parent_type,
            is_archived=g.is_archived,
            total=counts.get("total", 0),
            resolve=counts.get("resolve"),
            children=[],
        )


    def _build_doc(self, doc_groups, doc_children, counts_by_group, dict_group):
        result = []
        for g in doc_groups:
            node = self._to_node(g, counts_by_group.get(str(g.id), {}))
            dict_group[str(g.id)] = node
            result.append(node)

            # gắn children vào đúng parent thông qua dict_group (O(n), không query lại)
        for c in doc_children:
            node = self._to_node(c, counts_by_group.get(str(c.id), {}))
            dict_group[str(c.id)] = node
            parent = dict_group.get(str(c.parent_id))
            if parent is not None:
                parent.children.append(node)
        return result

    def _build_bug(self, bug_groups, counts_by_group, dict_group):
        result = []
        for g in bug_groups:
            node = self._to_node(g, counts_by_group.get(str(g.id), {"total": 0, "resolve": 0}))
            dict_group[str(g.id)] = node
            result.append(node)

        # bug không thuộc group nào -> node ảo "DEFAULT" (id=None), lấy từ nguồn đếm riêng

        return result

    def _build_tc(self, tc_groups, counts_by_group, dict_group):
        result = []
        for g in tc_groups:
            node = self._to_node(g, counts_by_group.get(str(g.id), {"total": 0, "resolve": 0}))
            dict_group[str(g.id)] = node
            result.append(node)
        return result

    # ------------------------------------------------------------------ #
    # Đếm theo group - chỉ dùng find()/to_list() có sẵn, gom bằng dict trong Python
    # ------------------------------------------------------------------ #
    async def _count_document_items_by_group(self,group_ids: list[str]) -> dict[str, dict]:
        """Dùng cho todo + doc: total document item theo group_id (1 query)."""
        if not group_ids:
            return {}
        filters = FilterDocumentItem(group_id=group_ids, offset=0, limit=1)
        items, total = await self.repository.get_all_document_items(filters)
        # print("items:", items)
        print("filters:", filters)
        counts: dict = {}
        for item in items:
            bucket = counts.setdefault(item.group_id, {"total": 0})
            bucket["total"] += 1
        return counts

    async def _count_bug_work_items_by_group(self,group_ids: list[str]) -> dict[str, dict]:
        """
        Bug THUỘC group: total + resolve (status VERIFIED) theo từng group_id.
        2 query đơn giản: 1 lấy total, 1 lấy verified - lọc theo group in group_ids.
        """
        if not group_ids:
            return {}

        filters = FilterWorkItemModel(offset=0, limit=1, group=group_ids, type=[WorkItemType.BUG])

        all_bugs = await self.work_item_repository.filter_work_item_for_order(filters)


        counts: dict[str, dict] = {}
        for bug in all_bugs:
            bucket = counts.setdefault(bug.group, {"total": 0, "resolve": 0})
            bucket["total"] += 1
            if bug.status == BugStatusEnum.VERIFIED:
                bucket["resolve"] += 1

        return counts

    async def _count_default_bug_work_items(self,project_id: str) -> dict:
        """
        Bug MẶC ĐỊNH của project: bug type=BUG nhưng không thuộc group nào (group is None).
        Response khác bug theo group (không có id thật) nên tách riêng, không gom chung.
        2 query đơn giản: total + verified.
        """


        filters = FilterWorkItemModel(offset=0, limit=1, project=[project_id], type=[WorkItemType.BUG])

        all_bugs = await self.work_item_repository.filter_work_item_for_order(filters)

        total = len(all_bugs)
        resolve = 0

        for bug in all_bugs:
            if bug.status == BugStatusEnum.VERIFIED:
                resolve += 1

        return {"total": total, "resolve": resolve}

    async def _count_tc_results_by_group(self,group_ids: list[str], owner_id:str) -> dict[str, dict]:
        """
        TC: group -> item (DocumentItem) -> result (DocumentResult).
        total = tổng số result, resolve = số result có evaluate = PASS.
        2 query đơn giản (item rồi result), gom theo group bằng dict trong Python.
        """
        if not group_ids:
            return {}

        filters = FilterDocumentItem(group_id=group_ids, offset=0, limit=1)
        items, total = await self.repository.get_all_document_items(filters)

        item_id_to_group = {str(i.id): i.group_id for i in items}
        item_ids = list(item_id_to_group.keys())
        filter_result = FilterDocumentResult(offset=0, limit=len(item_id_to_group), parent_id=item_ids, owner_id=[owner_id])
        results, total_result = await self.document_result_repository.get_all_document_result(filter_result)

        counts: dict[str, dict] = {}
        for r in results:
            group_id = item_id_to_group.get(r.parent_id)
            if group_id is None:
                continue
            bucket = counts.setdefault(group_id, {"total": 0, "resolve": 0})
            bucket["total"] += 1
            if r.evaluate and r.evaluate == DocumentResultEvaluate.PASS:
                bucket["resolve"] += 1
        return counts

    async def statistic_doc_item(self, filters: FilterDocumentItem):
        statistic_doc_item = await self.repository.statistic_document_item(filters)
        return ResponsePaginatedModel(data=statistic_doc_item, total=len(statistic_doc_item), offset=filters.offset,)
