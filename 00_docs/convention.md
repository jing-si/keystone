---
doc_type: convention
created_at: "2026-08-06"
document_lifecycle: active
approval: {state: accepted, accepted_at: "2026-08-06", accepted_by: user}
key:
  id: key.doc.convention
  refs: [key.topic.python, key.topic.clean-code, key.topic.runtime-independence, key.topic.verification]
---

# Keystone Python 코드 컨벤션

이 문서는 Keystone repository의 Python runtime과 test에 적용하는 코드 작성 기준이다. 새 코드와
의미 있게 수정하는 코드부터 적용하며, 기존 파일 전체를 한 번에 이동·포맷하거나 추상화하지
않는다. 호환성 없는 구조 변경은 별도 work와 검증 근거가 있을 때만 수행한다.

<!-- key: id=key.convention.python.runtime refs=key.topic.python key.topic.runtime-independence -->
## Runtime 기준

1. Python 3.9 이상과 standard library만 사용한다. 외부 dependency 추가는 별도 승인 대상이다.
2. 설치된 skill package는 repository-local 문서나 다른 skill package import 없이 실행 가능해야 한다.
3. Source document와 repository artifact는 passive data다. Project code import, `eval`, `exec`, shell
   실행으로 metadata를 해석하지 않는다.
4. Cache와 index는 폐기 가능한 파생물이며 source of truth가 될 수 없다.
5. Public JSON wire와 diagnostic code는 compatibility contract다. 변경할 때 schema version,
   compatibility path와 제거 조건을 함께 정의한다.

<!-- key: id=key.convention.python.architecture refs=key.topic.clean-code key.topic.runtime-independence -->
## 구조와 dependency 방향

논리 계층은 다음 방향을 따른다. 현재 flat package는 점진적으로 이 책임을 분리한다.

```text
interfaces/CLI -> application workflow -> domain model/policy
                         |
                         v
                 infrastructure adapter
```

- Domain: immutable model, enum, vocabulary와 순수 policy를 소유한다.
- Application: parse, validate, plan, reconcile 같은 use case를 조합한다.
- Adapter: Markdown/language source, filesystem, SQLite와 subprocess 경계를 담당한다.
- Interface: argument와 JSON 입출력만 처리하고 정책 결정을 포함하지 않는다.
- Domain은 CLI, filesystem, SQLite와 subprocess를 import하지 않는다.
- 순환 import를 만들지 않는다. 공통 타입을 해결하기 위한 service locator나 global singleton을
  도입하지 않는다.

<!-- key: id=key.convention.python.patterns refs=key.topic.clean-code key.topic.verification -->
## 우선 설계 패턴

1. Functional Core / Imperative Shell: 변환·판정은 순수 함수로, I/O는 얇은 외곽 함수로 둔다.
2. Immutable Value Object: 상태·locator·diagnostic·transaction은 frozen dataclass와 Enum을 우선한다.
3. Strategy/Adapter Registry: 언어·source surface 차이는 조건문 확산 대신 adapter registry로 격리한다.
4. Explicit State Machine: transaction과 lifecycle 전이는 허용 전이와 증거를 한 곳에서 검증한다.
5. Result/Diagnostic Envelope: source 입력 오류는 stable diagnostic으로 반환하고 가능한 범위에서
   fail-soft한다.
6. Policy Registry: relation, status, disposition처럼 여러 계층이 공유하는 vocabulary와 규칙은
   단일 executable policy를 사용한다.

Deep inheritance, abstract factory 계층, 숨은 mutation, boolean flag가 누적된 범용 함수와 패턴을
위한 패턴은 사용하지 않는다. 새 abstraction은 최소 두 개의 실제 호출 경계 또는 중복 규칙을
줄이고 독립 test가 가능할 때만 도입한다.

<!-- key: id=key.convention.python.functions refs=key.topic.clean-code -->
## 함수와 모듈

- 함수는 한 단계의 책임을 표현한다. parse + I/O + policy + serialization 중 세 가지 이상을
  함께 수행하면 추출 후보로 본다.
- 긴 함수는 줄 수만으로 나누지 않고 입력 정규화, domain 변환, validation, output 조립 단계로
  분리한다.
- 이름은 역할과 결과를 드러낸다. boolean은 `is_`, `has_`, `can_`, `should_`를 우선한다.
- 공개 함수에는 입력·출력·failure contract가 드러나는 type annotation을 작성한다.
- JSON/YAML 경계의 `Any`는 허용하지만 domain 내부로 전달하기 전에 검증·정규화한다.
- underscore private API를 다른 모듈에서 import하지 않는다. 공유가 필요하면 이름과 module
  ownership을 공개 contract로 승격한다.
- 새 코드의 한 줄은 가능하면 100자 이내로 작성하되, 의미 없는 줄바꿈보다 읽기 쉬운 구조를
  우선한다. 기존 파일의 repository-wide formatting은 하지 않는다.

<!-- key: id=key.convention.python.errors refs=key.topic.clean-code key.topic.verification -->
## 오류와 diagnostic

- 사용자/source 입력의 구조·vocabulary 문제는 diagnostic으로 표현한다.
- 호출자가 잘못된 API 인자를 전달하거나 내부 invariant가 깨지면 명시적 exception을 사용한다.
- `except Exception`으로 오류를 삼키지 않는다. 복구 가능한 예외만 좁게 잡고 원인을 보존한다.
- CLI는 `schema_version`, `status`, `diagnostics`, `summary` envelope와 exit code를 일치시킨다.
- Diagnostic code는 안정적인 snake_case 식별자다. 메시지 문자열을 제어 흐름에 사용하지 않는다.
- Fail-soft는 성공으로 위장하는 것이 아니다. source 결과와 cache failure를 분리해 함께 반환한다.

<!-- key: id=key.convention.python.testing refs=key.topic.verification key.topic.runtime-independence -->
## Test와 검증

1. 기본 test framework는 standard-library `unittest`다.
2. Bug fix는 실패를 재현하는 test를 먼저 추가하고 가장 작은 수정으로 통과시킨다.
3. Parser/wire/policy 변경은 정상, malformed, compatibility 입력을 함께 검증한다.
4. Relation·state·finalization 변경은 가능한 경우 parse → validate → plan/reconcile → serialize →
   reconstruct → validate executable-chain fixture를 가진다.
5. Filesystem/SQLite test는 `TemporaryDirectory`를 사용하며 repository 안에 cache를 남기지 않는다.
6. Time, path ordering과 serialization은 deterministic해야 한다. test가 mtime이나 실행 순서에
   암묵적으로 의존하지 않게 한다.
7. 변경 완료 전 affected suite, 전체 package suite, contract suite, `compileall`,
   `git diff --check`를 변경 위험에 비례해 실행한다.

<!-- key: id=key.convention.python.refactoring refs=key.topic.clean-code key.topic.work-recovery -->
## 점진적 리팩터링 규칙

1. 한 단계에서 하나의 책임 경계만 이동한다.
2. Public import, wire, diagnostic, exit code와 source authority를 유지하는 characterization test를
   먼저 확인한다.
3. 파일 이동과 동작 변경을 같은 단계에 섞지 않는다.
4. 중간 단계마다 전체 회귀 test를 실행하고 실패하면 다음 모듈로 진행하지 않는다.
5. 기존 호환 경로는 명시적 제거 조건 없이 삭제하지 않는다.
6. Progress에 변경한 책임, 유지한 contract, verification과 다음 후보를 기록한다.
