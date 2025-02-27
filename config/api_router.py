from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, SimpleRouter

from sme_ptrf_apps import __version__
from sme_ptrf_apps.core.api.views import (
    AssociacoesViewSet,
    AtasViewSet,
    DemonstrativoFinanceiroViewSet,
    MembroAssociacaoViewSet,
    PeriodosViewSet,
    PrestacoesContasViewSet,
    RelacaoBensViewSet,
    ProcessosAssociacaoViewSet,
    UnidadesViewSet,
    ConciliacoesViewSet,
    NotificacaoViewSet,
    DresViewSet,
    TiposDevolucaoAoTesouroViewSet,
    TiposContaViewSet,
    ComentariosAnalisesPrestacoesViewSet,
    AcaoAssociacaoViewSet,
    AcoesViewSet,
    ArquivoViewSet,
    TagsViewSet,
    ModelosCargasViewSet,
    AmbientesViewSet,
    ArquivosDownloadViewSet,
    TiposAcertoLancamentoViewSet,
    TiposAcertoDocumentoViewSet,
    AnalisesPrestacoesContasViewSet,
    PresentesAtaViewSet,
    AnaliseContaPrestacaoContaViewSet,
    ParametrosUeViewSet,
    AnaliseLancamentoPrestacaoContaViewSet,
    AnaliseDocumentoPrestacaoContaViewSet,
    FalhaGeracaoPcViewSet,
    SolicitacaoEncerramentoContaAssociacaoViewset,
    MotivoRejeicaoEncerramentoContaAssociacaoViewset
)
from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet
from sme_ptrf_apps.despesas.api.views.especificacoes_viewset import EspecificacaoMaterialServicoViewSet
from sme_ptrf_apps.despesas.api.views.fornecedores_viewset import FornecedoresViewSet
from sme_ptrf_apps.despesas.api.views.rateios_despesas_viewset import RateiosDespesasViewSet
from sme_ptrf_apps.despesas.api.views.tipos_custeio_viewset import TiposCusteioViewSet
from sme_ptrf_apps.despesas.api.views.motivos_pagamento_antecipado_viewset import MotivosPagamentoAntecipadoViewSet
from sme_ptrf_apps.dre.api.views import (
    FaqCategoriasViewSet,
    FaqsViewSet,
    TecnicosDreViewSet,
    AtribuicaoViewset,
    RelatoriosConsolidadosDREViewSet,
    JustificativasRelatoriosConsolidadosDreViewSet,
    MotivoAprovacaoRessalvaViewSet,
    MotivoReprovacaoViewSet,
    ComissoesViewSet,
    MembrosComissoesViewSet,
    AnosAnaliseRegularidadeViewSet,
    AtaParecerTecnicoViewset,
    ConsolidadosDreViewSet,
    ParametrosDreViewSet,
    ValoresReprogramadosViewSet,
    LaudaViewSet,
    ComentariosAnalisesConsolidadosDREViewSet,
    AnalisesDocumentosConsolidadoDreViewSet,
    AnalisesConsolidadoDreViewSet,
)
from sme_ptrf_apps.sme.api.views import (
    SaldosBancariosSMEViewSet,
    SaldosBancariosSmeDetalhesAsocciacoesViewSet,
    ParametrosSmeViewSet,
    ExportacoesDadosViewSet
)
from sme_ptrf_apps.receitas.api.views import ReceitaViewSet, RepasseViewSet, MotivosEstornoViewSet
from sme_ptrf_apps.users.api.views import (
    EsqueciMinhaSenhaViewSet,
    LoginView,
    RedefinirSenhaViewSet,
    UserViewSet, # TODO - Remover ao fim da implantação da nova gestão de usuários
    UsuariosViewSet,
    GruposViewSet
)

from sme_ptrf_apps.mandatos.api.views import MandatosViewSet, ComposicoesViewSet, OcupantesCargosViewSet, CargosComposicoesViewSet


@api_view()
def versao(request):
    return Response({"versao": __version__})


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("usuarios", UserViewSet) # TODO - Remover ao fim da implantação da nova gestão de usuários
router.register("usuarios-v2", UsuariosViewSet)
router.register("grupos", GruposViewSet)
router.register("despesas", DespesasViewSet)
router.register("especificacoes", EspecificacaoMaterialServicoViewSet)
router.register("rateios-despesas", RateiosDespesasViewSet)
router.register("receitas", ReceitaViewSet)
router.register("fornecedores", FornecedoresViewSet)
router.register("associacoes", AssociacoesViewSet)
router.register("repasses", RepasseViewSet, basename='repasses-pendentes')
router.register("periodos", PeriodosViewSet)
router.register("prestacoes-contas", PrestacoesContasViewSet)
router.register("demonstrativo-financeiro", DemonstrativoFinanceiroViewSet)
router.register("relacao-bens", RelacaoBensViewSet)
router.register("atas-associacao", AtasViewSet)
router.register("membros-associacao", MembroAssociacaoViewSet)
router.register("esqueci-minha-senha", EsqueciMinhaSenhaViewSet)
router.register("redefinir-senha", RedefinirSenhaViewSet)
router.register("processos-associacao", ProcessosAssociacaoViewSet)
router.register("unidades", UnidadesViewSet)
router.register("tecnicos-dre", TecnicosDreViewSet)
router.register("faq-categorias", FaqCategoriasViewSet)
router.register("faqs", FaqsViewSet)
router.register("atribuicoes", AtribuicaoViewset)
router.register("conciliacoes", ConciliacoesViewSet, basename='conciliacoes')
router.register("notificacoes", NotificacaoViewSet)
router.register("dres", DresViewSet)
router.register("tipos-devolucao-ao-tesouro", TiposDevolucaoAoTesouroViewSet)
router.register("tipos-conta", TiposContaViewSet)
router.register("comentarios-de-analises", ComentariosAnalisesPrestacoesViewSet)
router.register("relatorios-consolidados-dre", RelatoriosConsolidadosDREViewSet)
router.register("justificativas-relatorios-consolidados-dre", JustificativasRelatoriosConsolidadosDreViewSet)
router.register("motivos-aprovacao-ressalva", MotivoAprovacaoRessalvaViewSet)
router.register("motivos-reprovacao", MotivoReprovacaoViewSet)
router.register("acoes-associacoes", AcaoAssociacaoViewSet)
router.register("acoes", AcoesViewSet)
router.register("arquivos", ArquivoViewSet)
router.register("tags", TagsViewSet)
router.register("modelos-cargas", ModelosCargasViewSet)
router.register("tipos-custeio", TiposCusteioViewSet)
router.register("ambientes", AmbientesViewSet)
router.register("saldos-bancarios-sme", SaldosBancariosSMEViewSet)
router.register("saldos-bancarios-sme-detalhes", SaldosBancariosSmeDetalhesAsocciacoesViewSet)
router.register("arquivos-download", ArquivosDownloadViewSet)
router.register("tipos-acerto-lancamento", TiposAcertoLancamentoViewSet)
router.register("tipos-acerto-documento", TiposAcertoDocumentoViewSet)
router.register("analises-prestacoes-contas", AnalisesPrestacoesContasViewSet)
router.register("presentes-ata", PresentesAtaViewSet)
router.register("analises-conta-prestacao-conta", AnaliseContaPrestacaoContaViewSet)
router.register("analises-lancamento-prestacao-conta", AnaliseLancamentoPrestacaoContaViewSet)
router.register("analises-documento-prestacao-conta", AnaliseDocumentoPrestacaoContaViewSet)
router.register("comissoes", ComissoesViewSet)
router.register("membros-comissoes", MembrosComissoesViewSet)
router.register("anos-analise-regularidade", AnosAnaliseRegularidadeViewSet)
router.register("ata-parecer-tecnico", AtaParecerTecnicoViewset)
router.register("motivos-pagamento-antecipado", MotivosPagamentoAntecipadoViewSet)
router.register("motivos-estorno", MotivosEstornoViewSet)
router.register("consolidados-dre", ConsolidadosDreViewSet)
router.register("parametros-ue", ParametrosUeViewSet)
router.register("parametros-dre", ParametrosDreViewSet)
router.register("parametros-sme", ParametrosSmeViewSet)
router.register("valores-reprogramados", ValoresReprogramadosViewSet)
router.register("exportacoes-dados", ExportacoesDadosViewSet)
router.register("laudas", LaudaViewSet)
router.register("comentarios-de-analises-consolidados-dre", ComentariosAnalisesConsolidadosDREViewSet)
router.register("analises-documentos-consolidados-dre", AnalisesDocumentosConsolidadoDreViewSet)
router.register("analises-consolidados-dre", AnalisesConsolidadoDreViewSet)
router.register("falhas-geracao-pc", FalhaGeracaoPcViewSet)
router.register("solicitacoes-encerramento-conta", SolicitacaoEncerramentoContaAssociacaoViewset)
router.register("motivos-rejeicao-encerramento-conta", MotivoRejeicaoEncerramentoContaAssociacaoViewset)
router.register("mandatos", MandatosViewSet)
router.register("composicoes", ComposicoesViewSet)
router.register("ocupantes-cargos", OcupantesCargosViewSet)
router.register("cargos-composicao", CargosComposicoesViewSet)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("versao", versao),
    path("login", LoginView.as_view()),
]
