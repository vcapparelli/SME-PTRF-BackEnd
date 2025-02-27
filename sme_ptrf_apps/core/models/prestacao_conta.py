import logging

from datetime import date

from django.db import models
from django.db.models import Q
from django.db import transaction
from django.db.models.aggregates import Sum

from sme_ptrf_apps.core.models import Ata
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.dre.models import Atribuicao

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

logger = logging.getLogger(__name__)


class PrestacaoConta(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_NAO_APRESENTADA = 'NAO_APRESENTADA'
    STATUS_NAO_RECEBIDA = 'NAO_RECEBIDA'
    STATUS_RECEBIDA = 'RECEBIDA'
    STATUS_EM_ANALISE = 'EM_ANALISE'
    STATUS_DEVOLVIDA = 'DEVOLVIDA'
    STATUS_DEVOLVIDA_RETORNADA = 'DEVOLVIDA_RETORNADA'
    STATUS_DEVOLVIDA_RECEBIDA = 'DEVOLVIDA_RECEBIDA'
    STATUS_APROVADA = 'APROVADA'
    STATUS_APROVADA_RESSALVA = 'APROVADA_RESSALVA'
    STATUS_REPROVADA = 'REPROVADA'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'

    STATUS_NOMES = {
        STATUS_NAO_APRESENTADA: 'Não apresentada',
        STATUS_NAO_RECEBIDA: 'Não recebida',
        STATUS_RECEBIDA: 'Recebida',
        STATUS_EM_ANALISE: 'Em análise',
        STATUS_DEVOLVIDA: 'Devolvida para acertos',
        STATUS_DEVOLVIDA_RETORNADA: 'Apresentada após acertos',
        STATUS_DEVOLVIDA_RECEBIDA: 'Recebida após acertos',
        STATUS_APROVADA: 'Aprovada',
        STATUS_APROVADA_RESSALVA: 'Aprovada com ressalvas',
        STATUS_REPROVADA: 'Reprovada',
        STATUS_EM_PROCESSAMENTO: 'Em processamento'
    }

    STATUS_CHOICES = (
        (STATUS_NAO_APRESENTADA, STATUS_NOMES[STATUS_NAO_APRESENTADA]),
        (STATUS_NAO_RECEBIDA, STATUS_NOMES[STATUS_NAO_RECEBIDA]),
        (STATUS_RECEBIDA, STATUS_NOMES[STATUS_RECEBIDA]),
        (STATUS_EM_ANALISE, STATUS_NOMES[STATUS_EM_ANALISE]),
        (STATUS_DEVOLVIDA, STATUS_NOMES[STATUS_DEVOLVIDA]),
        (STATUS_DEVOLVIDA_RETORNADA, STATUS_NOMES[STATUS_DEVOLVIDA_RETORNADA]),
        (STATUS_DEVOLVIDA_RECEBIDA, STATUS_NOMES[STATUS_DEVOLVIDA_RECEBIDA]),
        (STATUS_APROVADA, STATUS_NOMES[STATUS_APROVADA]),
        (STATUS_APROVADA_RESSALVA, STATUS_NOMES[STATUS_APROVADA_RESSALVA]),
        (STATUS_REPROVADA, STATUS_NOMES[STATUS_REPROVADA]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
    )

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='prestacoes_de_conta')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='prestacoes_de_conta_da_associacao',
                                   blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_APRESENTADA
    )

    data_recebimento = models.DateField('data de recebimento pela DRE', blank=True, null=True)

    data_recebimento_apos_acertos = models.DateField('data de recebimento pela DRE após acertos', blank=True, null=True)

    data_ultima_analise = models.DateField('data da última análise pela DRE', blank=True, null=True)

    motivos_reprovacao = models.ManyToManyField('dre.MotivoReprovacao', blank=True)

    outros_motivos_reprovacao = models.TextField('Outros motivos para reprovação pela DRE', blank=True, default='')

    motivos_aprovacao_ressalva = models.ManyToManyField('dre.MotivoAprovacaoRessalva', blank=True)

    outros_motivos_aprovacao_ressalva = models.TextField('Outros motivos para aprovação com ressalvas pela DRE',
                                                         blank=True, default='')

    analise_atual = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.SET_NULL,
                                      related_name='+',
                                      blank=True, null=True)

    recomendacoes = models.TextField('Recomendações para aprovação com ressalvas pela DRE', blank=True, default='')

    publicada = models.BooleanField('Publicada', blank=True, null=True, default=False)

    consolidado_dre = models.ForeignKey('dre.ConsolidadoDRE', on_delete=models.SET_NULL,
                                        related_name='prestacoes_de_conta_do_consolidado_dre',
                                        blank=True, null=True)

    justificativa_pendencia_realizacao = models.TextField('Justificativa de pendências de realização de ajustes.',
                                                          blank=True, default='')

    status_anterior_a_retificacao = models.CharField(
        'Status anterior a retificacao',
        max_length=20,
        blank=True,
        null=True,
        default=None
    )

    @property
    def tecnico_responsavel(self):
        atribuicoes = Atribuicao.search(
            **{'unidade__uuid': self.associacao.unidade.uuid, 'periodo__uuid': self.periodo.uuid})
        if atribuicoes.exists():
            return atribuicoes.first().tecnico
        else:
            return None

    @property
    def total_devolucao_ao_tesouro(self):
        return self.devolucoes_ao_tesouro_da_prestacao.all().aggregate(Sum('valor'))['valor__sum'] or 0

    @property
    def total_devolucao_ao_tesouro_str(self):
        return f'{self.total_devolucao_ao_tesouro:.2f}'.replace('.',
                                                                ',') if self.devolucoes_ao_tesouro_da_prestacao.count() > 0 else 'Não'

    @property
    def em_retificacao(self):
        if self.consolidado_dre:
            return self.consolidado_dre.eh_retificacao

        return False

    @property
    def pode_desfazer_retificacao(self):
        if self.em_retificacao:
            if self.status == PrestacaoConta.STATUS_RECEBIDA:
                return True
            else:
                return False
        else:
            return None

    @property
    def tooltip_nao_pode_desfazer_retificacao(self):
        if not self.em_retificacao:
            return None

        if self.pode_desfazer_retificacao:
            return None
        else:
            return "Essa PC não pode ser removida da retificação pois sua análise já foi iniciada."

    @property
    def get_tooltip_nao_pode_retificar(self):
        if self.em_retificacao:
            return "Esta PC foi retificada em outra publicação."
        else:
            return None

    @property
    def pc_concluida(self):
        status_de_conlusao = [
            self.STATUS_APROVADA_RESSALVA,
            self.STATUS_APROVADA,
            self.STATUS_REPROVADA
        ]

        return self.status in status_de_conlusao

    @property
    def tipos_de_consolidados_disponiveis(self):
        tipos_disponiveis = {
            "pre_original": "PRE_ORIGINAL",
            "original": "ORIGINAL",
            "retificacao": "RETIFICACAO",
            "retificacao_da_retificacao": "RETIFICACAO_DA_RETIFICACAO"
        }

        return tipos_disponiveis

    @property
    def get_tipo_consolidado_vinculado(self):
        tipo_consolidado = None

        tipos_disponiveis = self.tipos_de_consolidados_disponiveis

        if self.consolidado_dre:
            if self.consolidado_dre.consolidado_retificado:
                # tenho um original, portanto sou uma retificacao
                tipo_consolidado = tipos_disponiveis["retificacao"]

                if self.consolidado_dre.consolidado_retificado.consolidado_retificado:
                    # o meu original tem um original, portanto sou uma retificacao de retificacao
                    tipo_consolidado = tipos_disponiveis["retificacao_da_retificacao"]
            else:
                # não tenho um original, portanto sou o original
                tipo_consolidado = tipos_disponiveis["original"]
        else:
            # Não tenho um consolidado ainda, portanto serei um original
            tipo_consolidado = tipos_disponiveis["pre_original"]

        return tipo_consolidado

    @property
    def get_mensagem_consolidado_tipo_original(self):
        tipo_relatorio = "Única" if self.consolidado_dre.sequencia_de_publicacao == 0 \
            else f'Parcial #{self.consolidado_dre.sequencia_de_publicacao}'

        mensagem = f"Essa PC consta da Publicação {tipo_relatorio}"

        return mensagem

    @property
    def get_mensagem_consolidado_tipo_retificacao(self):
        mensagem = ""

        if self.status == self.STATUS_RECEBIDA or self.status == self.STATUS_EM_ANALISE:
            tipo_relatorio = "Única" if self.consolidado_dre.consolidado_retificado.sequencia_de_publicacao == 0 \
                else f'Parcial #{self.consolidado_dre.consolidado_retificado.sequencia_de_publicacao}'

            mensagem = f"Essa PC consta da Publicação {tipo_relatorio}"

        elif self.pc_concluida:
            data_publicacao = self.consolidado_dre.get_data_publicacao_do_consolidado_original
            data_publicacao_formatada = data_publicacao.strftime('%d/%m/%Y') if data_publicacao else ""

            if self.publicada:
                mensagem = f"Essa PC consta da Retificação da publicação de {data_publicacao_formatada}"
            else:
                mensagem = f"Essa PC constará da Retificação da publicação de {data_publicacao_formatada}"

        return mensagem

    @property
    def get_mensagem_consolidado_tipo_retificacao_da_retificacao(self):
        mensagem = ""

        if self.status == self.STATUS_RECEBIDA or self.status == self.STATUS_EM_ANALISE:
            data_publicacao = self.consolidado_dre.consolidado_retificado.get_data_publicacao_do_consolidado_original
            data_publicacao_formatada = data_publicacao.strftime('%d/%m/%Y') if data_publicacao else ""

            mensagem = f"Essa PC consta da publicação retificadora de {data_publicacao_formatada}"

        elif self.pc_concluida:
            if self.publicada:
                data_publicacao = self.consolidado_dre.get_data_publicacao_do_consolidado_original
                data_publicacao_formatada = data_publicacao.strftime('%d/%m/%Y') if data_publicacao else ""

                mensagem = f"Essa PC consta da publicação retificadora de {data_publicacao_formatada}"
            else:
                data_publicacao = self.consolidado_dre.consolidado_retificado.get_data_publicacao_do_consolidado_original
                data_publicacao_formatada = data_publicacao.strftime('%d/%m/%Y') if data_publicacao else ""

                mensagem = f"Essa PC constará da retificação da publicação retificadora de {data_publicacao_formatada}"

        return mensagem

    @property
    def get_referencia_do_consolidado(self):
        mensagem = ""
        tipo_consolidado = self.get_tipo_consolidado_vinculado
        tipos_disponiveis = self.tipos_de_consolidados_disponiveis

        if tipo_consolidado == tipos_disponiveis["pre_original"]:
            mensagem = ""

        elif tipo_consolidado == tipo_consolidado == tipos_disponiveis["original"]:
            mensagem = self.get_mensagem_consolidado_tipo_original

        elif tipo_consolidado == tipos_disponiveis["retificacao"]:
            mensagem = self.get_mensagem_consolidado_tipo_retificacao

        elif tipo_consolidado == tipos_disponiveis["retificacao_da_retificacao"]:
            mensagem = self.get_mensagem_consolidado_tipo_retificacao_da_retificacao

        return mensagem

    @property
    def pc_publicada_no_diario_oficial(self):
        if self.consolidado_dre:
            return True if self.consolidado_dre.data_publicacao and self.consolidado_dre.pagina_publicacao else False

        return False

    def __str__(self):
        return f"{self.periodo} - {self.status}"

    def atrelar_consolidado_dre(self, consolidado_dre):
        self.consolidado_dre = consolidado_dre
        self.save()
        return self

    def passar_para_publicada(self):
        self.publicada = True
        self.save()
        return self

    def apaga_fechamentos(self):
        logging.info('Apagando fechamentos da prestação de contas')
        for fechamento in self.fechamentos_da_prestacao.all():
            fechamento.delete()

    def apaga_relacao_bens(self):
        for relacao in self.relacoes_de_bens_da_prestacao.all():
            relacao.delete()

    def apaga_demonstrativos_financeiros(self):
        for demonstrativo in self.demonstrativos_da_prestacao.all():
            demonstrativo.delete()

    def ultima_ata(self):
        return self.atas_da_prestacao.filter(tipo_ata='APRESENTACAO', previa=False).last()

    def ultima_ata_retificacao(self):
        return self.atas_da_prestacao.filter(tipo_ata='RETIFICACAO', previa=False).last()

    def ultima_analise(self):
        from ..models import AnalisePrestacaoConta
        ultima_analise = AnalisePrestacaoConta.objects.filter(prestacao_conta=self).last()
        return ultima_analise

    def concluir(self, e_retorno_devolucao=False, justificativa_acertos_pendentes=''):
        from ..models import DevolucaoPrestacaoConta
        from ..services.notificacao_services import marcar_como_lidas_notificacoes_de_devolucao_da_pc
        if e_retorno_devolucao:
            self.status = self.STATUS_DEVOLVIDA_RETORNADA
            ultima_devolucao = DevolucaoPrestacaoConta.objects.filter(prestacao_conta=self).order_by('id').last()
            ultima_devolucao.data_retorno_ue = date.today()
            ultima_devolucao.save()
        else:
            self.status = self.STATUS_NAO_RECEBIDA
        self.justificativa_pendencia_realizacao = justificativa_acertos_pendentes
        self.save()
        if e_retorno_devolucao:
            marcar_como_lidas_notificacoes_de_devolucao_da_pc(prestacao_de_contas=self)
        return self

    def receber(self, data_recebimento):
        self.data_recebimento = data_recebimento
        self.status = self.STATUS_RECEBIDA
        self.save()
        return self

    def receber_apos_acertos(self, data_recebimento_apos_acertos):
        self.data_recebimento_apos_acertos = data_recebimento_apos_acertos
        self.status = self.STATUS_DEVOLVIDA_RECEBIDA
        self.save()
        return self

    def desfazer_recebimento(self):
        self.data_recebimento = None
        self.status = self.STATUS_NAO_RECEBIDA
        self.save()
        return self

    def desfazer_recebimento_apos_acertos(self):
        self.data_recebimento_apos_acertos = None
        self.status = self.STATUS_DEVOLVIDA_RETORNADA
        self.save()
        return self

    def atualizar_comentarios_de_analise_sem_pc(self):
        from sme_ptrf_apps.core.models import ComentarioAnalisePrestacao
        comentarios_de_analise_relacionados_sem_pc = ComentarioAnalisePrestacao.objects.filter(Q(associacao=self.associacao) & \
                                                                                               Q(periodo=self.periodo) & \
                                                                                               Q(prestacao_conta__isnull=True))
        print('comentarios_de_analise_relacionados_sem_pc', comentarios_de_analise_relacionados_sem_pc)
        comentarios_de_analise_relacionados_sem_pc.update(prestacao_conta=self, associacao=None, periodo=None)

    def get_contas_com_movimento(self, add_sem_movimento_com_saldo=False):
        from sme_ptrf_apps.core.models import ContaAssociacao
        from sme_ptrf_apps.receitas.models import Receita
        from sme_ptrf_apps.despesas.models import RateioDespesa
        contas = ContaAssociacao.objects.filter(associacao=self.associacao).order_by('id')

        contas_com_movimento = []
        for conta in contas:
            tem_receitas_no_periodo = Receita.receitas_da_conta_associacao_no_periodo(
                conta_associacao=conta,
                periodo=self.periodo,
                inclui_inativas=True,
            ).exists()

            tem_gastos_no_periodo = RateioDespesa.rateios_da_conta_associacao_no_periodo(
                conta_associacao=conta,
                periodo=self.periodo,
                incluir_inativas=True,
            ).exists()

            if not tem_receitas_no_periodo and not tem_gastos_no_periodo and add_sem_movimento_com_saldo:
                tem_saldo_no_periodo = self.fechamentos_da_prestacao.filter(conta_associacao=conta).filter(
                    Q(saldo_reprogramado_custeio__gt=0) | Q(saldo_reprogramado_capital__gt=0) | Q(
                        saldo_reprogramado_livre__gt=0)).exists()
            else:
                tem_saldo_no_periodo = False

            if tem_receitas_no_periodo or tem_gastos_no_periodo or tem_saldo_no_periodo:
                contas_com_movimento.append(conta)

        return contas_com_movimento

    @transaction.atomic
    def analisar(self):
        from . import AnalisePrestacaoConta
        from ..services.analise_prestacao_conta_service import copia_ajustes_entre_analises

        analise_anterior = AnalisePrestacaoConta.objects.filter(prestacao_conta=self).order_by('-id').first()

        analise_atual = AnalisePrestacaoConta.objects.create(prestacao_conta=self)

        self.status = self.STATUS_EM_ANALISE
        self.analise_atual = analise_atual
        self.save()

        if analise_anterior:
            copia_ajustes_entre_analises(analise_origem=analise_anterior, analise_destino=analise_atual)

        return self

    @transaction.atomic
    def desfazer_analise(self):
        if self.analise_atual:
            self.analise_atual.delete()
            self.analise_atual = None

        self.data_ultima_analise = None
        self.status = self.STATUS_RECEBIDA
        self.save()
        return self

    def em_processamento(self):
        self.status = self.STATUS_EM_PROCESSAMENTO
        self.save()
        return self

    @transaction.atomic
    def salvar_devolucoes_ao_tesouro(self, devolucoes_ao_tesouro_da_prestacao=[]):
        from ..models.devolucao_ao_tesouro import DevolucaoAoTesouro
        from ..models.tipo_devolucao_ao_tesouro import TipoDevolucaoAoTesouro
        from ...despesas.models.despesa import Despesa

        for devolucao in devolucoes_ao_tesouro_da_prestacao:
            tipo_devolucao = TipoDevolucaoAoTesouro.by_uuid(devolucao['tipo'])
            despesa = Despesa.by_uuid(devolucao['despesa'])
            devolucao_uuid = devolucao['uuid']

            if devolucao_uuid:
                registro_devolucao = DevolucaoAoTesouro.objects.get(uuid=devolucao_uuid)

                registro_devolucao.prestacao_conta = self
                registro_devolucao.tipo = tipo_devolucao
                registro_devolucao.despesa = despesa
                registro_devolucao.data = devolucao['data']
                registro_devolucao.devolucao_total = devolucao['devolucao_total']
                registro_devolucao.motivo = devolucao['motivo']
                registro_devolucao.valor = devolucao['valor']
                registro_devolucao.visao_criacao = devolucao['visao_criacao']

                registro_devolucao.save()
            else:
                DevolucaoAoTesouro.objects.create(
                    prestacao_conta=self,
                    tipo=tipo_devolucao,
                    despesa=despesa,
                    data=devolucao['data'],
                    devolucao_total=devolucao['devolucao_total'],
                    motivo=devolucao['motivo'],
                    valor=devolucao['valor'],
                    visao_criacao=devolucao['visao_criacao'],
                )

        return self

    def apagar_devolucoes_ao_tesouro(self, devolucoes_ao_tesouro_a_apagar):
        from ..models.devolucao_ao_tesouro import DevolucaoAoTesouro

        for devolucao in devolucoes_ao_tesouro_a_apagar:
            if devolucao['uuid']:
                DevolucaoAoTesouro.objects.get(uuid=devolucao['uuid']).delete()

        return self

    @transaction.atomic
    def salvar_analise(self, analises_de_conta_da_prestacao=None, resultado_analise=None,
                       motivos_aprovacao_ressalva=[], outros_motivos_aprovacao_ressalva='', motivos_reprovacao=[],
                       outros_motivos_reprovacao='', recomendacoes=''):

        self.data_ultima_analise = date.today()

        if resultado_analise:
            self.status = resultado_analise

        if resultado_analise and self.analise_atual:
            self.analise_atual.status = resultado_analise
            self.analise_atual.save()

        self.motivos_aprovacao_ressalva.set(motivos_aprovacao_ressalva)
        self.outros_motivos_aprovacao_ressalva = outros_motivos_aprovacao_ressalva

        self.motivos_reprovacao.set(motivos_reprovacao)
        self.outros_motivos_reprovacao = outros_motivos_reprovacao

        self.recomendacoes = recomendacoes

        self.save()

        return self

    @transaction.atomic
    def devolver(self, data_limite_ue):
        from ..services.notificacao_services import notificar_prestacao_de_contas_devolvida_para_acertos
        from ..models import DevolucaoPrestacaoConta
        devolucao = DevolucaoPrestacaoConta.objects.create(
            prestacao_conta=self,
            data=date.today(),
            data_limite_ue=data_limite_ue
        )

        devolucao_requer_alteracoes = False

        if self.analise_atual:
            devolucao_requer_alteracoes = self.analise_atual.verifica_se_requer_alteracao_em_lancamentos(considera_realizacao=False)
            self.analise_atual.devolucao_prestacao_conta = devolucao
            self.analise_atual.status = self.STATUS_DEVOLVIDA
            self.analise_atual.save()

        self.analise_atual = None
        self.justificativa_pendencia_realizacao = ""
        self.save()

        if devolucao_requer_alteracoes:
            logging.info('A devolução de PC requer alterações e por isso deve apagar os seus fechamentos.')
            self.apaga_fechamentos()

        notificar_prestacao_de_contas_devolvida_para_acertos(self, data_limite_ue)
        return self

    @transaction.atomic
    def concluir_analise(self, resultado_analise, analises_de_conta_da_prestacao, motivos_aprovacao_ressalva,
                         outros_motivos_aprovacao_ressalva, data_limite_ue, motivos_reprovacao,
                         outros_motivos_reprovacao, recomendacoes):

        from ..services.notificacao_services import notificar_prestacao_de_contas_aprovada

        from ..services.notificacao_services import notificar_prestacao_de_contas_aprovada_com_ressalvas

        from ..services.notificacao_services import notificar_prestacao_de_contas_reprovada

        prestacao_atualizada = self.salvar_analise(resultado_analise=resultado_analise,
                                                   analises_de_conta_da_prestacao=analises_de_conta_da_prestacao,
                                                   motivos_aprovacao_ressalva=motivos_aprovacao_ressalva,
                                                   outros_motivos_aprovacao_ressalva=outros_motivos_aprovacao_ressalva,
                                                   motivos_reprovacao=motivos_reprovacao,
                                                   outros_motivos_reprovacao=outros_motivos_reprovacao,
                                                   recomendacoes=recomendacoes)

        if resultado_analise == PrestacaoConta.STATUS_DEVOLVIDA:
            prestacao_atualizada = prestacao_atualizada.devolver(data_limite_ue=data_limite_ue)

        if resultado_analise == PrestacaoConta.STATUS_APROVADA:
            try:
                notificar_prestacao_de_contas_aprovada(self)
            except Exception as erro:
                logger.error(f'Houve um erro ao notificar aprovação da PC. {erro}')

        if resultado_analise == PrestacaoConta.STATUS_APROVADA_RESSALVA:
            try:
                notificar_prestacao_de_contas_aprovada_com_ressalvas(self, motivos_aprovacao_ressalva,
                                                                     outros_motivos_aprovacao_ressalva)
            except Exception as erro:
                logger.error(f'Houve um erro ao notificar aprovação com ressalva da PC. {erro}')

        if resultado_analise == PrestacaoConta.STATUS_REPROVADA:
            try:
                notificar_prestacao_de_contas_reprovada(self, motivos_reprovacao, outros_motivos_reprovacao)
            except Exception as erro:
                logger.error(f'Houve um erro ao notificar reprovação da PC. {erro}')

        return prestacao_atualizada

    def desfazer_conclusao_analise(self):
        self.motivos_aprovacao_ressalva.set([])
        self.outros_motivos_aprovacao_ressalva = ''
        self.motivos_reprovacao.set([])
        self.outros_motivos_reprovacao = ''
        self.recomendacoes = ''
        self.status = self.STATUS_EM_ANALISE

        if self.consolidado_dre and not self.consolidado_dre.eh_retificacao:
            self.consolidado_dre.desvincular_pc_do_consolidado(self)
            self.consolidado_dre = None

        self.save()
        return self

    def pode_devolver(self):
        if self.analise_atual:
            requer_alteracao_em_lancamento = self.analise_atual.verifica_se_requer_alteracao_em_lancamentos(False)

            if not requer_alteracao_em_lancamento:
                return True

        pode_rebrir_pc = not self.associacao.fechamentos_associacao.filter(
            periodo__referencia__gt=self.periodo.referencia
        ).exists()
        return pode_rebrir_pc

    @classmethod
    @transaction.atomic
    def reabrir(cls, uuid):
        logger.info(f'Apagando a prestação de contas de uuid {uuid}.')
        try:
            prestacao_de_conta = cls.by_uuid(uuid=uuid)

            ata_da_pc = prestacao_de_conta.atas_da_prestacao.first()

            if ata_da_pc:
                ata_da_pc.prestacao_conta = None
                ata_da_pc.previa = True
                ata_da_pc.arquivo_pdf = None
                ata_da_pc.status_geracao_pdf = Ata.STATUS_NAO_GERADO
                ata_da_pc.save()

            prestacao_de_conta.apaga_fechamentos()
            prestacao_de_conta.apaga_relacao_bens()
            prestacao_de_conta.apaga_demonstrativos_financeiros()
            prestacao_de_conta.delete()
            logger.info(f'Prestação de contas de uuid {uuid} foi apagada.')
            return True
        except:
            logger.error(f'Houve algum erro ao tentar apagar a PC de uuid {uuid}.')
            return False

    @classmethod
    def abrir(cls, periodo, associacao):
        prestacao_de_conta, _ = cls.objects.get_or_create(
            periodo=periodo,
            associacao=associacao,
            defaults={
                'status': cls.STATUS_NAO_APRESENTADA
            }
        )
        prestacao_de_conta.atualizar_comentarios_de_analise_sem_pc()
        return prestacao_de_conta

    @classmethod
    def by_periodo(cls, associacao, periodo):
        return cls.objects.filter(associacao=associacao, periodo=periodo).first()

    @classmethod
    def dashboard(
        cls,
        periodo_uuid,
        dre_uuid,
        add_aprovado_ressalva=False,
        add_info_devolvidas_retornadas=False,
        apenas_nao_publicadas=False,
    ):
        """
        Retorna um dicionário com as informações para o dashboard de prestação de contas.

        :param periodo_uuid: UUID do período que será utilizado para filtrar as prestações de contas.

        :param dre_uuid: UUID da DRE que será utilizado para filtrar as prestações de contas.

        :param add_aprovado_ressalva: True para retornar a quantidade de aprovados com ressalva separadamente ou
        False para retornar a quantidade de aprovadas com ressalva somada a quantidade de aprovadas

        :param add_info_devolvidas_retornadas: True para retornar a quantidade de devolvidas retornadas no card de
        devolução.

        :param apenas_nao_publicadas: True para retornar apenas as prestações de contas que não foram publicadas.
        """
        from ..models import Associacao, Periodo, Unidade

        periodo = Periodo.by_uuid(periodo_uuid)
        dre = Unidade.by_uuid(dre_uuid)

        titulos_por_status = {
            cls.STATUS_NAO_RECEBIDA: "Prestações de contas não recebidas",
            cls.STATUS_RECEBIDA: "Prestações de contas recebidas aguardando análise",
            cls.STATUS_EM_ANALISE: "Prestações de contas em análise",
            cls.STATUS_DEVOLVIDA: "Prestações de conta devolvidas para acertos",
            cls.STATUS_APROVADA: "Prestações de contas aprovadas",
            cls.STATUS_REPROVADA: "Prestações de contas reprovadas",
        }

        if add_aprovado_ressalva:
            titulos_por_status[cls.STATUS_APROVADA_RESSALVA] = "Prestações de contas aprovadas com ressalvas"

        cards = []
        if not apenas_nao_publicadas:
            qs = cls.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid)
        else:
            qs = cls.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid,
                                    publicada=False)

        quantidade_pcs_apresentadas = 0
        for status, titulo in titulos_por_status.items():
            if status == cls.STATUS_NAO_RECEBIDA:
                continue

            quantidade_status = qs.filter(status=status).count()

            if status == cls.STATUS_APROVADA and not add_aprovado_ressalva:
                quantidade_status += qs.filter(status=cls.STATUS_APROVADA_RESSALVA).count()

            if status == cls.STATUS_DEVOLVIDA:
                quantidade_status += qs.filter(
                    status__in=[cls.STATUS_DEVOLVIDA_RETORNADA, cls.STATUS_DEVOLVIDA_RECEBIDA]).count()

            quantidade_pcs_apresentadas += quantidade_status

            if status == cls.STATUS_DEVOLVIDA and add_info_devolvidas_retornadas:
                quantidade_retornadas = qs.filter(status=cls.STATUS_DEVOLVIDA_RETORNADA).count()
                card = {
                    "titulo": titulo,
                    "quantidade_prestacoes": quantidade_status,
                    "quantidade_retornadas": quantidade_retornadas,
                    "status": status
                }
            else:
                card = {
                    "titulo": titulo,
                    "quantidade_prestacoes": quantidade_status,
                    "status": status
                }
            cards.append(card)

        associacoes_dre = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre)

        quantidade_unidades_dre = associacoes_dre.count()

        quantidade_pcs_nao_apresentadas = quantidade_unidades_dre - quantidade_pcs_apresentadas

        card_nao_recebidas = {
            "titulo": titulos_por_status['NAO_RECEBIDA'],
            "quantidade_prestacoes": quantidade_pcs_nao_apresentadas,
            "quantidade_nao_recebida": qs.filter(status=cls.STATUS_NAO_RECEBIDA).count(),
            "status": 'NAO_RECEBIDA'
        }
        cards.insert(0, card_nao_recebidas)
        return cards

    @classmethod
    def quantidade_por_status_sme(cls, periodo_uuid, numero_bruto_nao_apresentadas=False):

        from ..models import Periodo, Associacao
        periodo = Periodo.by_uuid(periodo_uuid)

        qtd_por_status = {
            cls.STATUS_NAO_RECEBIDA: 0,
            cls.STATUS_RECEBIDA: 0,
            cls.STATUS_EM_ANALISE: 0,
            cls.STATUS_DEVOLVIDA: 0,
            cls.STATUS_APROVADA: 0,
            cls.STATUS_APROVADA_RESSALVA: 0,
            cls.STATUS_REPROVADA: 0,
            cls.STATUS_NAO_APRESENTADA: 0,
            'TOTAL_UNIDADES': 0
        }

        qs = cls.objects.filter(periodo__uuid=periodo.uuid)


        quantidade_pcs_apresentadas = 0
        qtd_por_status['TOTAL_UNIDADES'] = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo).count()

        for status in qtd_por_status.keys():
            if status == 'TOTAL_UNIDADES' or status == cls.STATUS_NAO_APRESENTADA:
                continue

            quantidade_status = qs.filter(status=status).count()
            quantidade_pcs_apresentadas += quantidade_status
            qtd_por_status[status] = quantidade_status

        quantidade_pcs_nao_apresentadas = qtd_por_status['TOTAL_UNIDADES'] - quantidade_pcs_apresentadas
        qtd_por_status[cls.STATUS_NAO_APRESENTADA] = quantidade_pcs_nao_apresentadas

        return qtd_por_status

    @classmethod
    def quantidade_por_status_por_dre(cls, periodo_uuid, numero_bruto_nao_apresentadas=False):

        from ..models import Unidade, Associacao, Periodo, Associacao
        periodo = Periodo.by_uuid(periodo_uuid)

        qtd_por_status_dre = []
        for dre in Unidade.dres.all().order_by('sigla'):

            qtd_por_status = {
                cls.STATUS_NAO_RECEBIDA: 0,
                cls.STATUS_RECEBIDA: 0,
                cls.STATUS_EM_ANALISE: 0,
                cls.STATUS_DEVOLVIDA: 0,
                cls.STATUS_APROVADA: 0,
                cls.STATUS_APROVADA_RESSALVA: 0,
                cls.STATUS_REPROVADA: 0,
                cls.STATUS_NAO_APRESENTADA: 0,
                'TOTAL_UNIDADES': 0
            }

            qs = cls.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre.uuid)

            quantidade_pcs_apresentadas = 0
            qtd_por_status['TOTAL_UNIDADES'] = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).count()

            for status in qtd_por_status.keys():
                if status == 'TOTAL_UNIDADES' or status == cls.STATUS_NAO_APRESENTADA:
                    continue

                quantidade_status = qs.filter(status=status).count()
                quantidade_pcs_apresentadas += quantidade_status
                qtd_por_status[status] = quantidade_status

            quantidade_pcs_nao_apresentadas = qtd_por_status['TOTAL_UNIDADES'] - quantidade_pcs_apresentadas
            qtd_por_status[cls.STATUS_NAO_APRESENTADA] = quantidade_pcs_nao_apresentadas

            periodo_completo = (
                qtd_por_status[PrestacaoConta.STATUS_NAO_RECEBIDA] == 0
                and qtd_por_status[PrestacaoConta.STATUS_RECEBIDA] == 0
                and qtd_por_status[PrestacaoConta.STATUS_EM_ANALISE] == 0
                and qtd_por_status[PrestacaoConta.STATUS_DEVOLVIDA] == 0
            )

            if not numero_bruto_nao_apresentadas:
                qtd_por_status[PrestacaoConta.STATUS_NAO_RECEBIDA] += qtd_por_status[cls.STATUS_NAO_APRESENTADA]

            qtd_por_status_dre.append(
                {
                    'dre': {
                        'uuid': dre.uuid,
                        'sigla': dre.sigla,
                        'nome': dre.nome
                    },
                    'cards': qtd_por_status,
                    'periodo_completo': periodo_completo
                }
            )

        return qtd_por_status_dre

    @classmethod
    def _status_nao_selecionaveis(cls):
        return [cls.STATUS_EM_PROCESSAMENTO]

    @classmethod
    def status_to_json(cls):
        result = [{
            'id': choice[0],
            'nome': choice[1]
        } for choice in cls.STATUS_CHOICES if choice[0] not in cls._status_nao_selecionaveis()]

        return result

    class Meta:
        verbose_name = "Prestação de conta"
        verbose_name_plural = "09.0) Prestações de contas"
        unique_together = ['associacao', 'periodo']

auditlog.register(PrestacaoConta)
