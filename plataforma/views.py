from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import Pacientes, DadosPaciente, Refeicao, Opcao
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.messages import constants
from django.contrib import messages
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

@login_required(login_url='/auth/login')
def pacientes(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes})

    elif request.method == "POST":
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')

        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')

        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')

        pacientes = Pacientes.objects.filter(email=email)

        if pacientes.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')

        try:
            paciente = Pacientes(
                nome=nome,
                sexo=sexo,
                idade=idade,
                email=email,
                telefone=telefone,
                nutri=request.user
            )
            paciente.save()

            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso!')
            return redirect('/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema!')
            return redirect('/pacientes/')

@login_required(login_url='/auth/login')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})

@login_required(login_url='/auth/login')
def dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, "Este paciente não é seu!")
        return redirect('dados_paciente')
    
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente)
        return render(request, 'dados_paciente.html', {'paciente': paciente, 'dados_paciente': dados_paciente})
    
    elif request.method == "POST":
        altura = request.POST.get('altura')
        peso = request.POST.get('peso')
        gordura = request.POST.get('gordura')
        musculo = request.POST.get('musculo')
        hdl = request.POST.get('hdl')
        ldl = request.POST.get('ldl')
        ctotal = request.POST.get('ctotal')
        trigliceridios = request.POST.get('trigliceridios')

        if (len(altura.strip()) == 0) or (len(peso.strip()) == 0) or (len(gordura.strip()) == 0) or (len(musculo.strip()) == 0) or (len(hdl.strip()) == 0) or (len(ldl.strip()) == 0) or (len(ctotal.strip()) == 0) or (len(trigliceridios.strip()) == 0):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/dados_paciente/')

        try: 
            paciente = DadosPaciente(paciente=paciente,
                            data=datetime.now(),
                            peso=peso,
                            altura=altura,
                            gordura=gordura,
                            musculo=musculo,
                            hdl=hdl,
                            ldl=ldl,
                            ctotal=ctotal,
                            trigliceridios=trigliceridios)

            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrado com sucesso')
        except:
            messages.add_message(request, constants.ERROR, "Erro ao salvar os dados do paciente")
            return redirect('/dados_paciente/')
        return redirect(f'/dados_paciente/{id}')

@login_required(login_url='/auth/login')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")

    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos, 'labels': labels}
    return JsonResponse(data)

@login_required(login_url='/auth/login')
def plano_alimentar_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})

@login_required(login_url='/auth/login')
def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, "Esse paciente não é seu!")
        return redirect('plano_alimentar_listar')

    re = Refeicao.objects.filter(paciente=paciente).order_by('horario')
    opcao = Opcao.objects.all()
    if request.method == "GET":
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao': re, 'opcao': opcao})

@login_required(login_url='/auth/login')
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, "Esse paciente não é seu!")
        return redirect('/dados_paciente/')


    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('proteinas')

        r1 = Refeicao(
            paciente=paciente,
            titulo=titulo,
            horario=horario,
            carboidratos=carboidratos,
            proteinas=proteinas,
            gorduras=gorduras
        )

        r1.save()

        messages.add_message(request, constants.SUCCESS, "Refeição cadastrada!")
        return redirect(f'/plano_alimentar/{id_paciente}')

def opcao(request, id_paciente):
    id_refeicao = request.POST.get('refeicao')
    imagem = request.FILES.get('imagem')
    descricao = request.POST.get('descricao')

    op = Opcao(
        refeicao_id=id_refeicao,
        imagem=imagem,
        descricao=descricao
    )

    op.save()

    messages.add_message(request, constants.SUCCESS, "Opção cadastrada!")
    
    return redirect(f'/plano_alimentar/{id_paciente}')

def gerar_os(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    refeicao = Refeicao.objects.filter(paciente_id=id)
    opcao = Opcao.objects.all()
    
    refeicoes = [{'titulo': i.titulo, 'hora': i.horario.strftime('%H:%M'), 'id': i.id} for i in refeicao]
    opcoes = [{'descricao': i.descricao, 'ref_id': i.refeicao_id} for i in opcao]
    
    #PDF
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.set_fill_color(240,240,240)

    pdf.cell(0, 10, f'Plano Alimentar: {paciente}', 1, 1, 'C', 1)

    # Iterar sobre as refeições
    for refeicao in refeicoes:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Refeicao: {refeicao['titulo']}, Horário: {refeicao['hora']}", 1, 1, 'L', 1)

        # Filtrar as opções relacionadas a esta refeição
        opcoes_refeicao = [opcao for opcao in opcoes if opcao['ref_id'] == refeicao['id']]

        # Listar as opções
        pdf.set_font('Arial', '', 12)
        for opcao in opcoes_refeicao:
            pdf.multi_cell(0, 10, f"Opção: {opcao['descricao']}", 1, 'L')

    # Salvar o PDF em um arquivo
    pdf_content = pdf.output(dest='S').encode('latin1')
    pdf_bytes = BytesIO(pdf_content)

    return FileResponse(pdf_bytes, filename="os.pdf")
